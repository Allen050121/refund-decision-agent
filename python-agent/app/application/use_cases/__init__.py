"""
任务处理 Use Case
文档 5.2: 完整工作流执行
"""
import logging
import time
from datetime import datetime, timezone
from typing import Optional

from app.agent.state import AgentState
from app.application.ports import (
    TaskRepositoryPort,
    EventPublisherPort,
)
from app.domain.models.task import Task, TaskStatus
from app.domain.models.refund import RefundDecision, DecisionType

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProcessTaskUseCase:
    """
    处理售后任务用例
    文档 6.1: 消费 Redis 任务 -> 执行 LangGraph -> 保存结果 -> ACK
    """

    def __init__(
        self,
        task_repository: TaskRepositoryPort,
        event_publisher: EventPublisherPort,
    ):
        self.task_repository = task_repository
        self.event_publisher = event_publisher

    async def execute(self, task: Task) -> RefundDecision:
        """
        执行任务处理
        文档 6.1: 成功条件 (XACK 之前):
          1. Agent 结果持久化成功
          2. Token 和 Trace 摘要持久化成功
          3. 任务状态更新成功
          4. 最后执行 XACK
        """
        task_id = task.task_id
        start_time = time.time()

        try:
            # 1. 更新状态为处理中
            await self.task_repository.update_status(task_id, TaskStatus.PROCESSING)
            await self.event_publisher.publish_progress(task_id, "init", "started")

            # 2. 构建 Agent 初始状态
            state = AgentState(
                task_id=task.task_id,
                user_id=task.user_id,
                ticket_content=task.ticket_content,
                order_id=task.order_id,
                trace_context={
                    "trace_id": task.trace_id or task_id,
                    "task_id": task_id,
                    "started_at": utc_now().isoformat(),
                },
            )

            # 3. 执行 LangGraph 工作流
            from app.agent.graph import graph

            compiled_graph = graph.compile()
            final_state = await compiled_graph.ainvoke(state)

            # 4. 构建决策结果
            decision = self._build_decision(task_id, final_state, start_time)

            # 5. 持久化结果
            task.status = TaskStatus.COMPLETED
            task.result = decision.model_dump()
            task.completed_at = utc_now()
            await self.task_repository.save(task)

            # 6. 发布完成事件
            await self.event_publisher.publish_progress(task_id, "complete", "completed")

            logger.info(f"任务处理完成 | task_id={task_id} | decision={decision.decision}")
            return decision

        except Exception as e:
            logger.error(f"任务处理失败 | task_id={task_id} | error={e}")

            # 保存失败状态
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = utc_now()
            await self.task_repository.save(task)

            # 发布错误事件
            await self.event_publisher.publish(
                task_id,
                {
                    "type": "error",
                    "node": "workflow",
                    "error": str(e),
                    "timestamp": utc_now().isoformat(),
                },
            )

            raise

    def _build_decision(
        self, task_id: str, state: AgentState, start_time: float
    ) -> RefundDecision:
        """从最终状态构建决策结果"""
        elapsed = time.time() - start_time

        # 映射决策类型
        decision_type = DecisionEnum_to_DecisionType(state.decision)

        return RefundDecision(
            task_id=task_id,
            decision=decision_type,
            reason_code=state.reason_code.value if state.reason_code else None,
            rule_citations=state.rule_citations,
            evidence=state.evidence,
            risk_hints=state.risk_hints,
            model_calls=state.budget.get("used_model_calls", 0),
            tool_calls=state.budget.get("used_tool_calls", 0),
        )


def DecisionEnum_to_DecisionType(decision_enum) -> DecisionType:
    """将 Agent 状态中的决策枚举映射到领域决策类型"""
    from app.agent.state import DecisionEnum

    mapping = {
        DecisionEnum.REFUND_RECOMMENDED: DecisionType.REFUND_RECOMMENDED,
        DecisionEnum.REFUND_REJECTED: DecisionType.REFUND_REJECTED,
        DecisionEnum.NEED_MORE_INFORMATION: DecisionType.NEED_MORE_INFORMATION,
        DecisionEnum.WAIT_FOR_APPROVAL: DecisionType.WAIT_FOR_APPROVAL,
    }
    return mapping.get(decision_enum, DecisionType.NEED_MORE_INFORMATION)
