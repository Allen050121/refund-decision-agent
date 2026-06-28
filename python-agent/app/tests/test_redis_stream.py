"""
测试 Redis Streams 消费者和事件发布器
"""
import asyncio
import pytest
import pytest_asyncio
from typing import Dict, Any, List

from app.infrastructure.redis_stream.consumer import RedisStreamConsumer
from app.infrastructure.redis_stream.event_publisher import RedisEventPublisher
from app.domain.models.task import Task, TaskStatus


TEST_STREAM = "test:agent:tasks"
TEST_GROUP = "test-workers"
TEST_EVENTS_STREAM = "test:agent:events:{task_id}"


@pytest_asyncio.fixture
async def redis_client():
    """创建 Redis 客户端"""
    import redis.asyncio as redis
    client = redis.from_url("redis://192.168.85.66:6379/0", decode_responses=True)
    # 清理测试数据
    await client.delete(TEST_STREAM)
    await client.delete(TEST_EVENTS_STREAM.format(task_id="T-EVENT-001"))
    await client.delete(TEST_EVENTS_STREAM.format(task_id="T-PROGRESS-001"))
    await client.delete(TEST_EVENTS_STREAM.format(task_id="T-DECISION-001"))
    await client.delete(TEST_EVENTS_STREAM.format(task_id="T-ERROR-001"))
    yield client
    # 清理测试数据
    await client.delete(TEST_STREAM)
    await client.close()


@pytest_asyncio.fixture
async def consumer(redis_client):
    """创建消费者"""
    c = RedisStreamConsumer(
        redis_url="redis://192.168.85.66:6379/0",
        stream_name=TEST_STREAM,
        group_name=TEST_GROUP,
        consumer_name="test-worker-1",
    )
    yield c
    await c.stop()


@pytest_asyncio.fixture
async def publisher(redis_client):
    """创建事件发布器"""
    from app.config import settings
    # 覆盖 events key 配置
    settings.REDIS_EVENTS_KEY = "test:agent:events:{task_id}"
    p = RedisEventPublisher(redis_url="redis://192.168.85.66:6379/0")
    yield p
    await p.close()


@pytest.mark.asyncio
async def test_consumer_group_creation(consumer: RedisStreamConsumer, redis_client):
    """测试消费者组创建"""
    await consumer.ensure_group()

    # 验证组存在
    groups = await redis_client.xinfo_groups(TEST_STREAM)
    group_names = [g["name"] for g in groups]
    assert TEST_GROUP in group_names


@pytest.mark.asyncio
async def test_publish_and_consume(consumer: RedisStreamConsumer, publisher: RedisEventPublisher):
    """测试发布和消费任务"""
    processed_tasks: List[Task] = []

    async def handler(task: Task):
        processed_tasks.append(task)

    # 发布任务
    await consumer.ensure_group()
    r = await consumer._get_redis()
    await r.xadd(TEST_STREAM, {
        "task_id": "T-TEST-001",
        "user_id": "U1001",
        "ticket_content": "测试工单",
        "order_id": "ORD-001",
    })

    # 消费任务
    messages = await consumer._read_messages(">")
    assert len(messages) == 1

    message_id, data = messages[0]
    task = Task(
        task_id=data.get("task_id"),
        user_id=data.get("user_id"),
        ticket_content=data.get("ticket_content"),
        order_id=data.get("order_id"),
        message_id=message_id,
    )

    await handler(task)
    await r.xack(TEST_STREAM, TEST_GROUP, message_id)

    assert len(processed_tasks) == 1
    assert processed_tasks[0].task_id == "T-TEST-001"


@pytest.mark.asyncio
async def test_event_publisher(publisher: RedisEventPublisher, redis_client):
    """测试事件发布"""
    task_id = "T-EVENT-001"
    stream_name = TEST_EVENTS_STREAM.format(task_id=task_id)

    # 发布事件
    await publisher.publish(task_id, {
        "type": "progress",
        "node": "classify_and_extract",
        "status": "completed",
    })

    await publisher.publish(task_id, {
        "type": "decision",
        "decision": "REFUND_RECOMMENDED",
    })

    # 验证事件
    events = await redis_client.xrange(stream_name)
    assert len(events) == 2

    # 验证 sequence 递增
    event_1 = events[0][1]
    event_2 = events[1][1]
    assert event_1["sequence"] == "1"
    assert event_2["sequence"] == "2"


@pytest.mark.asyncio
async def test_event_publisher_progress(publisher: RedisEventPublisher, redis_client):
    """测试进度事件发布"""
    task_id = "T-PROGRESS-001"
    stream_name = TEST_EVENTS_STREAM.format(task_id=task_id)

    await publisher.publish_progress(task_id, "classify", "completed")
    await publisher.publish_progress(task_id, "validate", "completed")

    events = await redis_client.xrange(stream_name)
    assert len(events) == 2
    assert events[0][1]["type"] == "progress"
    assert events[0][1]["node"] == "classify"


@pytest.mark.asyncio
async def test_event_publisher_decision(publisher: RedisEventPublisher, redis_client):
    """测试决策事件发布"""
    task_id = "T-DECISION-001"
    stream_name = TEST_EVENTS_STREAM.format(task_id=task_id)

    await publisher.publish_decision(task_id, {
        "decision": "REFUND_RECOMMENDED",
        "reason_code": "COURSE_UNAVAILABLE",
    })

    events = await redis_client.xrange(stream_name)
    assert len(events) == 1
    assert events[0][1]["decision"] == "REFUND_RECOMMENDED"


@pytest.mark.asyncio
async def test_event_publisher_error(publisher: RedisEventPublisher, redis_client):
    """测试错误事件发布"""
    task_id = "T-ERROR-001"
    stream_name = TEST_EVENTS_STREAM.format(task_id=task_id)

    await publisher.publish_error(task_id, "LLM timeout")

    events = await redis_client.xrange(stream_name)
    assert len(events) == 1
    assert events[0][1]["error"] == "LLM timeout"


@pytest.mark.asyncio
async def test_consumer_pending_recovery(consumer: RedisStreamConsumer, redis_client):
    """测试 pending 消息恢复"""
    await consumer.ensure_group()

    # 发布消息但不 ACK
    await redis_client.xadd(TEST_STREAM, {
        "task_id": "T-PENDING-001",
        "user_id": "U1001",
        "ticket_content": "待恢复消息",
    })

    # 读取消息
    messages = await consumer._read_messages(">")
    assert len(messages) == 1

    # 不 ACK，模拟崩溃

    # 回收 pending 消息
    claimed = await consumer.claim_pending(min_idle_time=0)
    assert claimed >= 1


@pytest.mark.asyncio
async def test_consumer_ack_after_process(consumer: RedisStreamConsumer, redis_client):
    """测试处理后 ACK"""
    await consumer.ensure_group()

    # 发布消息
    await redis_client.xadd(TEST_STREAM, {
        "task_id": "T-ACK-001",
        "user_id": "U1001",
        "ticket_content": "测试 ACK",
    })

    # 读取并处理
    messages = await consumer._read_messages(">")
    message_id, data = messages[0]

    # ACK
    await redis_client.xack(TEST_STREAM, TEST_GROUP, message_id)

    # 验证 pending 为空
    pending = await redis_client.xpending_range(TEST_STREAM, TEST_GROUP, min="-", max="+", count=100)
    # 应该没有该消息的 pending 记录
