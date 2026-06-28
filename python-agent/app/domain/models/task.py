"""
任务领域模型
文档 6.1: 任务创建与消费
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态"""

    CREATED = "CREATED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


class TaskPriority(str, Enum):
    """任务优先级 - 文档 7.4: 流分区"""

    REALTIME = "REALTIME"
    BATCH = "BATCH"
    RETRY = "RETRY"
    DLQ = "DLQ"  # Dead Letter Queue


class Task(BaseModel):
    """
    售后任务
    文档 6.1: 任务消息格式
    """

    task_id: str = Field(..., description="任务 ID")
    user_id: str = Field(..., description="用户 ID")
    ticket_content: str = Field(..., description="工单内容")
    order_id: Optional[str] = Field(None, description="订单 ID")

    # 状态管理
    status: TaskStatus = Field(default=TaskStatus.CREATED)
    priority: TaskPriority = Field(default=TaskPriority.REALTIME)

    # 幂等性 - 文档 7.2
    idempotency_key: Optional[str] = Field(None, description="幂等键")

    # 重试与超时
    retry_count: int = Field(default=0, description="重试次数")
    max_retries: int = Field(default=3, description="最大重试次数")
    timeout_seconds: int = Field(default=300, description="超时时间（秒）")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(None, description="开始处理时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

    # 心跳 - 文档 6.1: XAUTOCLAIM 防误判
    last_heartbeat_at: Optional[datetime] = Field(None, description="最后心跳时间")

    # 结果
    result: Optional[dict] = Field(None, description="处理结果")
    error_message: Optional[str] = Field(None, description="错误信息")

    # Trace - 文档 10
    trace_id: Optional[str] = Field(None, description="追踪 ID")
    message_id: Optional[str] = Field(None, description="Redis 消息 ID")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
