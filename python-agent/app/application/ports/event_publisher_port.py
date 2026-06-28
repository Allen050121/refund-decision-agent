"""
事件发布 Port - 抽象接口
文档 6.3: 进度通知
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class EventPublisherPort(ABC):
    """
    事件发布抽象接口
    文档 6.3:
      - Python 写入结构化事件到 Redis Event Stream
      - Java 转换为 SSE 推送前端
      - 事件包含 eventId 和递增 sequence
    """

    @abstractmethod
    async def publish(self, task_id: str, event: Dict[str, Any]) -> None:
        """
        发布任务事件
        Args:
            task_id: 任务 ID
            event: 事件数据，包含:
              - eventId: 事件 ID
              - sequence: 递增序列号
              - type: 事件类型 (progress, decision, error, etc.)
              - data: 事件详情
        """
        ...

    @abstractmethod
    async def publish_progress(self, task_id: str, node_name: str, status: str, detail: str = "") -> None:
        """
        发布节点进度事件
        Args:
            task_id: 任务 ID
            node_name: LangGraph 节点名称
            status: 状态 (started, completed, failed)
            detail: 详情
        """
        ...
