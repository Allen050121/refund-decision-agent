"""
任务管理 API
文档 6.1: 任务创建与查询
"""
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent.state import AgentState, DecisionEnum
from app.domain.models.task import Task, TaskStatus

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

router = APIRouter()

# ============================================================
# 内存任务仓储（MVP 阶段，后续替换为 Redis/DB）
# ============================================================
_tasks_store: Dict[str, Task] = {}
_results_store: Dict[str, Dict[str, Any]] = {}


# ============================================================
# 请求/响应模型
# ============================================================
class TaskCreateRequest(BaseModel):
    """任务创建请求"""

    userId: str = Field(..., description="用户 ID")
    ticketContent: str = Field(..., description="工单内容")
    orderId: Optional[str] = Field(None, description="订单 ID")


class TaskCreateResponse(BaseModel):
    """任务创建响应"""

    taskId: str = Field(..., description="任务 ID")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="消息")


class TaskStatusResponse(BaseModel):
    """任务状态响应"""

    taskId: str
    status: str
    decision: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    errors: list[str] = []
    createdAt: Optional[str] = None
    completedAt: Optional[str] = None


# ============================================================
# API 端点
# ============================================================
@router.post("", response_model=TaskCreateResponse)
async def create_task(request: TaskCreateRequest):
    """
    创建售后任务
    文档 6.1: 接收工单 -> 创建任务 -> 执行 LangGraph -> 返回结果
    MVP 阶段同步执行，后续改为 Redis Streams 异步
    """
    task_id = f"T-{uuid.uuid4().hex[:12]}"

    task = Task(
        task_id=task_id,
        user_id=request.userId,
        ticket_content=request.ticketContent,
        order_id=request.orderId,
        status=TaskStatus.CREATED,
        trace_id=task_id,
    )

    # 保存到存储
    _tasks_store[task_id] = task

    logger.info(f"创建任务 | task_id={task_id} | user_id={request.userId}")

    # 异步执行工作流（使用 asyncio.run 确保在同步环境下也能执行）
    import asyncio
    try:
        # 检查是否已有事件循环在运行
        loop = asyncio.get_running_loop()
        if loop.is_running():
            # 在异步环境中使用 create_task
            asyncio.create_task(_execute_task(task))
        else:
            # 不应该到这里，但为了安全
            asyncio.run(_execute_task(task))
    except RuntimeError:
        # 没有事件循环，创建新的
        asyncio.run(_execute_task(task))

    return TaskCreateResponse(
        taskId=task_id,
        status="CREATED",
        message="任务已创建，正在处理中",
    )


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task(task_id: str):
    """查询任务状态和结果"""
    task = _tasks_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    result = _results_store.get(task_id)

    return TaskStatusResponse(
        taskId=task.task_id,
        status=task.status.value,
        decision=result.get("decision") if result else None,
        result=result,
        errors=task.error_message.split("|") if task.error_message else [],
        createdAt=task.created_at.isoformat() if task.created_at else None,
        completedAt=task.completed_at.isoformat() if task.completed_at else None,
    )


@router.get("", response_model=list[TaskStatusResponse])
async def list_tasks(limit: int = 20, offset: int = 0):
    """列出所有任务"""
    tasks = list(_tasks_store.values())
    tasks.sort(key=lambda t: t.created_at, reverse=True)
    tasks_page = tasks[offset : offset + limit]

    return [
        TaskStatusResponse(
            taskId=t.task_id,
            status=t.status.value,
            decision=_results_store.get(t.task_id, {}).get("decision"),
            result=_results_store.get(t.task_id),
            errors=t.error_message.split("|") if t.error_message else [],
            createdAt=t.created_at.isoformat() if t.created_at else None,
            completedAt=t.completed_at.isoformat() if t.completed_at else None,
        )
        for t in tasks_page
    ]


# ============================================================
# 内部方法
# ============================================================
async def _execute_task(task: Task) -> None:
    """
    执行 LangGraph 工作流
    文档 5.2: 完整节点流程
    """
    try:
        task.status = TaskStatus.PROCESSING
        task.started_at = utc_now()

        # 构建初始状态
        state = AgentState(
            task_id=task.task_id,
            user_id=task.user_id,
            ticket_content=task.ticket_content,
            order_id=task.order_id,
            trace_context={
                "trace_id": task.trace_id or task.task_id,
                "task_id": task.task_id,
                "started_at": utc_now().isoformat(),
            },
        )

        # 执行 LangGraph 工作流
        from app.agent.graph import graph

        compiled_graph = graph.compile()
        final_state = await compiled_graph.ainvoke(state)

        # ainvoke 返回 dict，需要用 dict 访问方式
        decision = final_state.get("decision")
        reason_code = final_state.get("reason_code")

        # 保存结果
        result = {
            "decision": decision.value if decision else None,
            "reason_code": reason_code.value if reason_code else None,
            "risk_hints": final_state.get("risk_hints", []),
            "rule_citations": final_state.get("rule_citations", []),
            "evidence": final_state.get("evidence", []),
            "errors": final_state.get("errors", []),
        }
        _results_store[task.task_id] = result

        # 更新任务状态
        task.status = TaskStatus.COMPLETED
        task.completed_at = utc_now()
        task.result = result

        logger.info(f"任务处理完成 | task_id={task.task_id} | decision={result.get('decision')}")

    except Exception as e:
        logger.error(f"任务处理失败 | task_id={task.task_id} | error={e}")
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        task.completed_at = utc_now()


def get_task_store() -> Dict[str, Task]:
    """获取任务存储（测试用）"""
    return _tasks_store


def get_results_store() -> Dict[str, Dict[str, Any]]:
    """获取结果存储（测试用）"""
    return _results_store
