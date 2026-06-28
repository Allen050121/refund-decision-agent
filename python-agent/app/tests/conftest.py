"""
测试 fixtures
"""
import pytest
import pytest_asyncio

from app.agent.state import AgentState, IntentEnum, ReasonCodeEnum
from app.infrastructure.llm.fake_client import FakeLLMClient
from app.infrastructure.retrieval.fake_retriever import FakeRetriever


@pytest.fixture
def fake_llm():
    """Fake LLM 客户端"""
    return FakeLLMClient()


@pytest.fixture
def fake_retriever():
    """Fake 规则检索器"""
    return FakeRetriever()


@pytest.fixture
def sample_state():
    """样本 Agent 状态"""
    return AgentState(
        task_id="T-001",
        user_id="U1001",
        ticket_content="我购买的Python课程打不开，一直显示加载中，要求退款",
        order_id="ORD-001",
        intent=IntentEnum.REFUND_REQUEST,
        reason_code=ReasonCodeEnum.COURSE_UNAVAILABLE,
    )


@pytest.fixture
def sample_order_snapshot():
    """样本订单快照"""
    return {
        "orderId": "ORD-001",
        "userId": "U1001",
        "status": "PAID",
        "totalAmount": 19900,
        "paymentMethod": "WECHAT",
        "courseId": "C-101",
        "createdAt": "2026-06-20T10:00:00",
    }


@pytest.fixture
def sample_learning_progress():
    """样本学习进度"""
    return {
        "orderId": "ORD-001",
        "userId": "U1001",
        "progressPercentage": 0,
        "lastStudiedAt": None,
        "totalStudyMinutes": 0,
    }
