"""
测试 LangGraph 工作流节点
"""
import pytest
import pytest_asyncio

from app.agent.state import AgentState, IntentEnum, ReasonCodeEnum, DecisionEnum
from app.agent.nodes import (
    classify_and_extract,
    validate_required_fields,
    query_business_data,
    retrieve_rules,
    check_eligibility,
    generate_recommendation,
    risk_gate,
    set_ports,
)
from app.infrastructure.llm.fake_client import FakeLLMClient
from app.infrastructure.retrieval.fake_retriever import FakeRetriever


@pytest.fixture(autouse=True)
def setup_ports():
    """每个测试前注入 Fake Port"""
    fake_llm = FakeLLMClient()
    fake_retriever = FakeRetriever()
    set_ports(llm=fake_llm, retrieval=fake_retriever)
    yield {"llm": fake_llm, "retriever": fake_retriever}
    set_ports(llm=None, retrieval=None)


# ============================================================
# 节点 1: classify_and_extract
# ============================================================
@pytest.mark.asyncio
async def test_classify_refund_request():
    """测试退款意图识别"""
    state = AgentState(
        task_id="T-001",
        user_id="U1001",
        ticket_content="我购买的课程打不开，要求退款",
    )
    result = await classify_and_extract(state)
    assert result["intent"] == IntentEnum.REFUND_REQUEST


@pytest.mark.asyncio
async def test_classify_course_unavailable():
    """测试课程不可用原因识别"""
    state = AgentState(
        task_id="T-002",
        user_id="U1002",
        ticket_content="课程打不开，无法观看",
    )
    result = await classify_and_extract(state)
    assert result.get("reason_code") == ReasonCodeEnum.COURSE_UNAVAILABLE


@pytest.mark.asyncio
async def test_classify_duplicate_purchase():
    """测试重复购买原因识别"""
    state = AgentState(
        task_id="T-003",
        user_id="U1003",
        ticket_content="我不小心买重了课程，申请退款",
    )
    result = await classify_and_extract(state)
    assert result.get("reason_code") == ReasonCodeEnum.DUPLICATE_PURCHASE


@pytest.mark.asyncio
async def test_classify_no_reason():
    """测试无理由退款识别"""
    state = AgentState(
        task_id="T-004",
        user_id="U1004",
        ticket_content="不想学了，退款",
    )
    result = await classify_and_extract(state)
    assert result.get("reason_code") == ReasonCodeEnum.NO_REASON


@pytest.mark.asyncio
async def test_classify_corrects_llm_general_with_deterministic_signal():
    """测试 LLM 泛化为 GENERAL 时，明确业务信号会被规则校正"""
    fake_llm = FakeLLMClient(
        responses=[
            {
                "content": {
                    "intent": "REFUND_REQUEST",
                    "reason_code": "GENERAL",
                    "confidence": 0.6,
                }
            }
        ]
    )
    set_ports(llm=fake_llm, retrieval=FakeRetriever())

    state = AgentState(
        task_id="T-004-A",
        user_id="U1004",
        ticket_content="课程一直打不开，视频故障，申请退款",
    )
    result = await classify_and_extract(state)

    assert result["intent"] == IntentEnum.REFUND_REQUEST
    assert result["reason_code"] == ReasonCodeEnum.COURSE_UNAVAILABLE


@pytest.mark.asyncio
async def test_classify_empty_ticket():
    """测试空工单内容"""
    state = AgentState(task_id="T-005", ticket_content="")
    result = await classify_and_extract(state)
    assert result["intent"] == IntentEnum.OTHER


# ============================================================
# 节点 2: validate_required_fields
# ============================================================
@pytest.mark.asyncio
async def test_validate_all_fields_present():
    """测试所有字段都存在"""
    state = AgentState(
        task_id="T-001",
        user_id="U1001",
        order_id="ORD-001",
        ticket_content="退款",
    )
    result = await validate_required_fields(state)
    assert result["missing_fields"] == []


@pytest.mark.asyncio
async def test_validate_missing_order_id():
    """测试缺少订单 ID"""
    state = AgentState(
        task_id="T-002",
        user_id="U1002",
        ticket_content="退款",
    )
    result = await validate_required_fields(state)
    assert "order_id" in result["missing_fields"]


@pytest.mark.asyncio
async def test_validate_missing_user_id():
    """测试缺少用户 ID"""
    state = AgentState(
        task_id="T-003",
        order_id="ORD-001",
        ticket_content="退款",
    )
    result = await validate_required_fields(state)
    assert "user_id" in result["missing_fields"]


@pytest.mark.asyncio
async def test_validate_missing_ticket_content():
    """测试缺少工单内容"""
    state = AgentState(
        task_id="T-004",
        user_id="U1004",
        order_id="ORD-001",
    )
    result = await validate_required_fields(state)
    assert "ticket_content" in result["missing_fields"]


# ============================================================
# 节点 4: retrieve_rules
# ============================================================
@pytest.mark.asyncio
async def test_retrieve_rules():
    """测试规则检索"""
    state = AgentState(
        task_id="T-001",
        user_id="U1001",
        ticket_content="课程打不开，退款",
        reason_code=ReasonCodeEnum.COURSE_UNAVAILABLE,
    )
    result = await retrieve_rules(state)
    assert "retrieved_rules" in result
    assert isinstance(result["retrieved_rules"], list)


@pytest.mark.asyncio
async def test_retrieve_rules_with_scenario_filter():
    """测试带场景过滤的规则检索"""
    state = AgentState(
        task_id="T-002",
        ticket_content="重复购买",
        reason_code=ReasonCodeEnum.DUPLICATE_PURCHASE,
    )
    result = await retrieve_rules(state)
    rules = result["retrieved_rules"]
    # FakeRetriever 会根据 scenario 过滤
    for rule in rules:
        assert rule.get("scenario") == "DUPLICATE_PURCHASE"


# ============================================================
# 节点 5: check_eligibility
# ============================================================
@pytest.mark.asyncio
async def test_check_eligibility_course_unavailable():
    """测试课程不可用 - 应退款"""
    state = AgentState(
        task_id="T-001",
        reason_code=ReasonCodeEnum.COURSE_UNAVAILABLE,
        order_snapshot={"status": "PAID", "totalAmount": 19900},
        retrieved_rules=[],
    )
    result = await check_eligibility(state)
    assert result["eligibility_result"]["eligible"] is True
    assert result["eligibility_result"]["decision_code"] == "COURSE_SERVICE_FAILURE"


@pytest.mark.asyncio
async def test_check_eligibility_expired_window():
    """测试超期退款 - 不应退款"""
    state = AgentState(
        task_id="T-002",
        reason_code=ReasonCodeEnum.EXPIRED_REFUND_WINDOW,
        order_snapshot={},
        retrieved_rules=[],
    )
    result = await check_eligibility(state)
    assert result["eligibility_result"]["eligible"] is False
    assert result["eligibility_result"]["decision_code"] == "REFUND_WINDOW_EXPIRED"


@pytest.mark.asyncio
async def test_check_eligibility_no_reason_needs_approval():
    """测试无理由退款 - 需审批"""
    state = AgentState(
        task_id="T-003",
        reason_code=ReasonCodeEnum.NO_REASON,
        order_snapshot={},
        retrieved_rules=[],
    )
    result = await check_eligibility(state)
    assert result["eligibility_result"]["approval_required"] is True


# ============================================================
# 节点 6: generate_recommendation
# ============================================================
@pytest.mark.asyncio
async def test_generate_recommendation_eligible():
    """测试符合资格 - 建议退款"""
    state = AgentState(
        task_id="T-001",
        eligibility_result={"eligible": True, "approval_required": False},
    )
    result = await generate_recommendation(state)
    assert result["decision"] in [DecisionEnum.REFUND_RECOMMENDED, DecisionEnum.WAIT_FOR_APPROVAL]


@pytest.mark.asyncio
async def test_generate_recommendation_not_eligible():
    """测试不符合资格 - 拒绝退款"""
    state = AgentState(
        task_id="T-002",
        eligibility_result={"eligible": False, "approval_required": False},
    )
    result = await generate_recommendation(state)
    assert result["decision"] == DecisionEnum.REFUND_REJECTED


@pytest.mark.asyncio
async def test_generate_recommendation_needs_approval():
    """测试需要审批"""
    state = AgentState(
        task_id="T-003",
        eligibility_result={"eligible": True, "approval_required": True},
    )
    result = await generate_recommendation(state)
    assert result["decision"] == DecisionEnum.WAIT_FOR_APPROVAL


# ============================================================
# 节点 7: risk_gate
# ============================================================
@pytest.mark.asyncio
async def test_risk_gate_normal():
    """测试正常情况 - 无风险"""
    state = AgentState(
        task_id="T-001",
        decision=DecisionEnum.REFUND_RECOMMENDED,
        eligibility_result={"approval_required": False},
        risk_hints=[],
        errors=[],
    )
    result = await risk_gate(state)
    assert result["decision"] == DecisionEnum.REFUND_RECOMMENDED


@pytest.mark.asyncio
async def test_risk_gate_permission_denied():
    """测试权限错误 - 应拒绝"""
    state = AgentState(
        task_id="T-002",
        decision=DecisionEnum.REFUND_RECOMMENDED,
        errors=["PERMISSION_DENIED: 无权访问此订单"],
        risk_hints=[],
    )
    result = await risk_gate(state)
    assert result["decision"] == DecisionEnum.REFUND_REJECTED


@pytest.mark.asyncio
async def test_risk_gate_conflicting_rules():
    """测试规则冲突 - 需审批"""
    state = AgentState(
        task_id="T-003",
        decision=DecisionEnum.REFUND_RECOMMENDED,
        risk_hints=["存在冲突规则，需人工审批"],
        errors=[],
    )
    result = await risk_gate(state)
    assert result["decision"] == DecisionEnum.WAIT_FOR_APPROVAL


@pytest.mark.asyncio
async def test_risk_gate_missing_fields_need_more_information():
    state = AgentState(
        task_id="T-005",
        intent=IntentEnum.REFUND_REQUEST,
        decision=DecisionEnum.REFUND_RECOMMENDED,
        missing_fields=["order_id"],
        risk_hints=[],
        errors=[],
    )
    result = await risk_gate(state)
    assert result["decision"] == DecisionEnum.NEED_MORE_INFORMATION
    assert any("order_id" in hint for hint in result["risk_hints"])


@pytest.mark.asyncio
async def test_risk_gate_other_intent_need_more_information():
    state = AgentState(
        task_id="T-006",
        intent=IntentEnum.OTHER,
        decision=DecisionEnum.REFUND_RECOMMENDED,
        risk_hints=[],
        errors=[],
    )
    result = await risk_gate(state)
    assert result["decision"] == DecisionEnum.NEED_MORE_INFORMATION


@pytest.mark.asyncio
async def test_risk_gate_approval_required():
    """测试资格结果中要求审批"""
    state = AgentState(
        task_id="T-004",
        decision=DecisionEnum.REFUND_RECOMMENDED,
        eligibility_result={"approval_required": True},
        risk_hints=[],
        errors=[],
    )
    result = await risk_gate(state)
    assert result["decision"] == DecisionEnum.WAIT_FOR_APPROVAL
