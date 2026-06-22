from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TaskRequest(BaseModel):
    """工单请求模型"""
    userId: str
    content: str


class TaskResponse(BaseModel):
    """任务响应模型"""
    taskId: str
    status: str
    message: str


@router.post("", response_model=TaskResponse)
def create_task(request: TaskRequest):
    """创建售后任务"""
    # TODO: 实现任务创建逻辑
    return TaskResponse(
        taskId="T1001",
        status="CREATED",
        message="任务已创建"
    )


@router.get("/{task_id}")
def get_task(task_id: str):
    """查询任务状态"""
    # TODO: 实现任务查询逻辑
    return {"taskId": task_id, "status": "PROCESSING"}
