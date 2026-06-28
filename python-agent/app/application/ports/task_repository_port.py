"""
任务仓储 Port - 抽象接口
"""
from abc import ABC, abstractmethod
from typing import Optional
from app.domain.models.task import Task, TaskStatus


class TaskRepositoryPort(ABC):
    """任务持久化抽象接口"""

    @abstractmethod
    async def save(self, task: Task) -> None:
        """保存任务"""
        ...

    @abstractmethod
    async def find_by_id(self, task_id: str) -> Optional[Task]:
        """根据 ID 查询任务"""
        ...

    @abstractmethod
    async def update_status(self, task_id: str, status: TaskStatus, **kwargs) -> None:
        """
        更新任务状态
        kwargs 可传 result, error_message 等
        """
        ...

    @abstractmethod
    async def update_heartbeat(self, task_id: str) -> None:
        """
        更新心跳
        文档 6.1: 长时间运行的任务必须更新心跳，避免被 XAUTOCLAIM 误判
        """
        ...
