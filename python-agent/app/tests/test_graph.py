"""
测试完整 LangGraph 工作流
"""
import pytest
import pytest_asyncio

from app.agent.state import AgentState, IntentEnum, ReasonCodeEnum, DecisionEnum
from app.agent.nodes import set_ports
from app.infrastructure.llm.fake_client import FakeLLMClient
from app.infrastructure.retrieval.fake_retriever import FakeRetriever


@pytest.fixture(autouse=True)
def setup_ports():
    """注入 Fake Port"""
    fake_llm = FakeLLMClient()
    fake_retriever = FakeRetriever()
    set_ports(llm=fake_llm, retrieval=fake_retriever)
    yield
    set_ports(llm=None, retrieval=None)


@pytest.mark.asyncio
async def test_full_workflow_refund_recommended():
    """测试完整工作流 - 课程不可用，建议退款"""
    state = AgentState(
        task_id="T-001",
        user_id="U1001",
        ticket_content="课程打不开，无法观看，申请退款",
        order_id="ORD-001",
    )

    from app.agent.graph import graph

    compiled = graph.compile()
    final_state = await compiled.ainvoke(state)

    # ainvoke 返回 dict
    assert final_state["intent"] == IntentEnum.REFUND_REQUEST
    assert final_state["reason_code"] == ReasonCodeEnum.COURSE_UNAVAILABLE
    assert final_state["decision"] in [
        DecisionEnum.REFUND_RECOMMENDED,
        DecisionEnum.WAIT_FOR_APPROVAL,
    ]


@pytest.mark.asyncio
async def test_full_workflow_refund_rejected():
    """测试完整工作流 - 超期退款，拒绝"""
    state = AgentState(
        task_id="T-002",
        user_id="U1002",
        ticket_content="超过30天了，想退款",
        order_id="ORD-002",
    )

    from app.agent.graph import graph

    compiled = graph.compile()
    final_state = await compiled.ainvoke(state)

    assert final_state["intent"] == IntentEnum.REFUND_REQUEST
    assert final_state["reason_code"] in [
        ReasonCodeEnum.EXPIRED_REFUND_WINDOW,
        ReasonCodeEnum.GENERAL,
    ]


@pytest.mark.asyncio
async def test_full_workflow_missing_fields():
    """测试完整工作流 - 缺少字段"""
    state = AgentState(
        task_id="T-003",
        ticket_content="我要退款",
        # 缺少 user_id 和 order_id
    )

    from app.agent.graph import graph

    compiled = graph.compile()
    final_state = await compiled.ainvoke(state)

    # 应该检测到缺失字段
    missing = final_state.get("missing_fields", [])
    assert len(missing) > 0
    assert "user_id" in missing or "order_id" in missing
    assert final_state["decision"] == DecisionEnum.NEED_MORE_INFORMATION


@pytest.mark.asyncio
async def test_full_workflow_other_intent_needs_more_information():
    state = AgentState(
        task_id="T-003-A",
        user_id="U1003",
        ticket_content="我想咨询一下 Java 课程大纲和上课时间",
    )

    from app.agent.graph import graph

    compiled = graph.compile()
    final_state = await compiled.ainvoke(state)

    assert final_state["intent"] == IntentEnum.OTHER
    assert final_state["decision"] == DecisionEnum.NEED_MORE_INFORMATION


@pytest.mark.asyncio
async def test_full_workflow_no_reason_needs_approval():
    """测试完整工作流 - 无理由退款需审批"""
    state = AgentState(
        task_id="T-004",
        user_id="U1004",
        ticket_content="不想学了，退款",
        order_id="ORD-004",
    )

    from app.agent.graph import graph

    compiled = graph.compile()
    final_state = await compiled.ainvoke(state)

    assert final_state["intent"] == IntentEnum.REFUND_REQUEST
    assert final_state["reason_code"] == ReasonCodeEnum.NO_REASON
    # 无理由退款应该需要审批
    assert final_state["decision"] in [
        DecisionEnum.WAIT_FOR_APPROVAL,
        DecisionEnum.REFUND_RECOMMENDED,
    ]


@pytest.mark.asyncio
async def test_workflow_error_tracking():
    """测试错误追踪"""
    state = AgentState(
        task_id="T-005",
        user_id="U1005",
        ticket_content="",
        order_id="ORD-005",
    )

    from app.agent.graph import graph

    compiled = graph.compile()
    final_state = await compiled.ainvoke(state)

    # 空工单不应崩溃
    assert final_state is not None
    assert final_state["task_id"] == "T-005"


@pytest.mark.asyncio
async def test_workflow_budget_tracking():
    """测试预算追踪"""
    state = AgentState(
        task_id="T-006",
        user_id="U1006",
        ticket_content="退款",
        order_id="ORD-006",
        budget={
            "max_model_calls": 10,
            "max_tool_calls": 15,
            "max_token_cost": 1.0,
            "used_model_calls": 0,
            "used_tool_calls": 0,
            "used_token_cost": 0.0,
        },
    )

    from app.agent.graph import graph

    compiled = graph.compile()
    final_state = await compiled.ainvoke(state)

    # 预算应该被更新
    budget = final_state.get("budget", {})
    assert "used_model_calls" in budget
    assert "used_tool_calls" in budget
