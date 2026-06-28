"""
Redis 事件发布器
文档 6.3: 进度通知
  - Event Stream: after-sale:agent:events:{taskId}
  - 事件包含 eventId 和递增 sequence
"""
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

import redis.asyncio as redis

from app.application.ports.event_publisher_port import EventPublisherPort
from app.config import settings

logger = logging.getLogger(__name__)


class RedisEventPublisher(EventPublisherPort):
    """
    Redis 事件发布器
    文档 6.3:
      - Python 写入结构化事件到 Redis Event Stream
      - Java 转换为 SSE 推送前端
      - 支持断线续传
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self._redis: Optional[redis.Redis] = None
        self._sequences: Dict[str, int] = {}  # task_id -> sequence

    async def _get_redis(self) -> redis.Redis:
        """懒初始化 Redis 连接"""
        if self._redis is None:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def publish(self, task_id: str, event: Dict[str, Any]) -> None:
        """
        发布事件到 Redis Stream
        文档 6.3: after-sale:agent:events:{taskId}
        """
        r = await self._get_redis()

        stream_name = settings.REDIS_EVENTS_KEY.format(task_id=task_id)

        # 递增 sequence
        self._sequences[task_id] = self._sequences.get(task_id, 0) + 1

        # 构建事件
        event_data = {
            "eventId": str(uuid.uuid4()),
            "sequence": str(self._sequences[task_id]),
            "timestamp": datetime.utcnow().isoformat(),
            **{k: str(v) if not isinstance(v, str) else v for k, v in event.items()},
        }

        await r.xadd(stream_name, event_data)
        logger.debug(f"事件已发布 | task_id={task_id} | sequence={event_data['sequence']}")

    async def publish_progress(
        self, task_id: str, node_name: str, status: str, detail: str = ""
    ) -> None:
        """
        发布节点进度事件
        文档 6.3: 进度通知
        """
        await self.publish(task_id, {
            "type": "progress",
            "node": node_name,
            "status": status,
            "detail": detail,
        })

    async def publish_decision(self, task_id: str, decision: Dict[str, Any]) -> None:
        """发布决策事件"""
        await self.publish(task_id, {
            "type": "decision",
            **decision,
        })

    async def publish_error(self, task_id: str, error: str) -> None:
        """发布错误事件"""
        await self.publish(task_id, {
            "type": "error",
            "error": error,
        })

    async def close(self) -> None:
        """关闭 Redis 连接"""
        if self._redis:
            await self._redis.close()
            self._redis = None
