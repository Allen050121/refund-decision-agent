"""
Redis Streams 任务消费者
文档 6.1: 消费者组设置
  stream: after-sale:agent:tasks
  group: after-sale-agent-workers
  consumer: worker-{instance-id}
文档 6.1:
  - 使用 XPENDING 和 XAUTOCLAIM 恢复崩溃消费者的任务
  - 长时间运行的任务必须更新心跳
"""
import asyncio
import logging
import socket
import uuid
from datetime import datetime, timezone
from typing import Optional, Callable, Awaitable, Dict, Any

import redis.asyncio as redis

from app.application.ports.task_repository_port import TaskRepositoryPort
from app.config import settings
from app.domain.models.task import Task, TaskStatus

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

# 回调类型: 接收 Task，返回处理结果
TaskHandler = Callable[[Task], Awaitable[None]]


class RedisStreamConsumer:
    """
    Redis Streams 消费者
    文档 6.1:
      - at-least-once 消费
      - 依赖业务幂等性保证副作用唯一性 (文档 7.2)
      - 消费幂等: task_id (文档 7.2)
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        stream_name: Optional[str] = None,
        group_name: str = "after-sale-agent-workers",
        consumer_name: Optional[str] = None,
        batch_size: int = 1,
        block_timeout: int = 5000,  # 毫秒
    ):
        self.redis_url = redis_url or settings.REDIS_URL
        self.stream_name = stream_name or settings.REDIS_STREAM_NAME
        self.group_name = group_name
        self.consumer_name = consumer_name or f"worker-{socket.gethostname()}-{uuid.uuid4().hex[:8]}"
        self.batch_size = batch_size
        self.block_timeout = block_timeout

        self._redis: Optional[redis.Redis] = None
        self._running = False
        self._handler: Optional[TaskHandler] = None
        self._task_repository: Optional[TaskRepositoryPort] = None

    async def _get_redis(self) -> redis.Redis:
        """懒初始化 Redis 连接"""
        if self._redis is None:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def ensure_group(self) -> None:
        """确保消费者组存在"""
        r = await self._get_redis()
        try:
            await r.xgroup_create(
                self.stream_name, self.group_name, id="0", mkstream=True
            )
            logger.info(f"消费者组已创建 | stream={self.stream_name} | group={self.group_name}")
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.debug(f"消费者组已存在 | group={self.group_name}")
            else:
                raise

    async def start(self, handler: TaskHandler, task_repository: TaskRepositoryPort) -> None:
        """
        启动消费循环
        Args:
            handler: 任务处理回调
            task_repository: 任务仓储（用于心跳更新）
        """
        self._handler = handler
        self._task_repository = task_repository
        self._running = True

        await self.ensure_group()
        logger.info(f"消费者启动 | consumer={self.consumer_name} | stream={self.stream_name}")

        # 先读取未确认的消息（恢复）
        last_id = "0"
        while self._running:
            try:
                messages = await self._read_messages(last_id)
                if messages:
                    for message_id, data in messages:
                        await self._process_message(message_id, data)
                    last_id = ">"  # 切换为只读新消息
                else:
                    last_id = ">"  # 无待处理消息，等待新消息
            except Exception as e:
                logger.error(f"消费循环异常: {e}")
                await asyncio.sleep(1)

    async def stop(self) -> None:
        """停止消费"""
        self._running = False
        if self._redis:
            await self._redis.aclose()
            self._redis = None
        logger.info("消费者已停止")

    async def _read_messages(self, last_id: str) -> list:
        """从 Redis Stream 读取消息"""
        r = await self._get_redis()

        try:
            results = await r.xreadgroup(
                groupname=self.group_name,
                consumername=self.consumer_name,
                streams={self.stream_name: last_id},
                count=self.batch_size,
                block=self.block_timeout,
            )
        except Exception:
            return []

        messages = []
        if results:
            for _stream_name, stream_messages in results:
                for msg_id, msg_data in stream_messages:
                    messages.append((msg_id, msg_data))
        return messages

    async def _process_message(self, message_id: str, data: Dict[str, Any]) -> None:
        """
        处理单条消息
        文档 6.1: 成功条件:
          1. Agent 结果持久化成功
          2. Token 和 Trace 摘要持久化成功
          3. 任务状态更新成功
          4. 最后执行 XACK
        """
        try:
            # 解析任务
            task = Task(
                task_id=data.get("task_id", ""),
                user_id=data.get("user_id", ""),
                ticket_content=data.get("ticket_content", ""),
                order_id=data.get("order_id"),
                message_id=message_id,
                trace_id=data.get("trace_id"),
            )

            logger.info(f"处理任务消息 | task_id={task.task_id} | message_id={message_id}")

            # 更新心跳
            task.last_heartbeat_at = utc_now()
            if self._task_repository:
                await self._task_repository.save(task)

            # 执行处理
            if self._handler:
                await self._handler(task)

            # 确认消息
            r = await self._get_redis()
            await r.xack(self.stream_name, self.group_name, message_id)
            logger.info(f"消息已确认 | message_id={message_id}")

        except Exception as e:
            logger.error(f"消息处理失败 | message_id={message_id} | error={e}")
            # 不 ACK，让消息留在 Pending 列表中等待重试或 XAUTOCLAIM

    async def claim_pending(self, min_idle_time: int = 60000) -> int:
        """
        回收空闲超时的待处理消息
        文档 6.1: XPENDING + XAUTOCLAIM
        Args:
            min_idle_time: 最小空闲时间（毫秒）
        Returns:
            回收的消息数量
        """
        r = await self._get_redis()

        try:
            # 检查 pending 消息
            pending = await r.xpending_range(
                self.stream_name,
                self.group_name,
                min="-",
                max="+",
                count=100,
            )

            if not pending:
                return 0

            # 回收空闲超时的消息
            _, claimed_messages, _ = await r.xautoclaim(
                self.stream_name,
                self.group_name,
                self.consumer_name,
                min_idle_time=min_idle_time,
                start_id="0-0",
                count=10,
            )

            count = len(claimed_messages)
            if count > 0:
                logger.info(f"回收了 {count} 条超时消息")

            return count
        except Exception as e:
            logger.error(f"回收 pending 消息失败: {e}")
            return 0
