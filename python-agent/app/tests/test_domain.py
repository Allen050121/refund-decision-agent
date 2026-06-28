"""
测试 Domain 层
"""
import pytest
from datetime import datetime

from app.domain.models.task import Task, TaskStatus, TaskPriority
from app.domain.models.refund import RefundDecision, RefundEligibility, DecisionType, RiskLevel
from app.domain.exceptions import (
    PermissionDeniedException,
    ResourceNotFoundException,
    BudgetExceededException,
)
from app.domain.policies import evaluate_refund_eligibility


# ============================================================
# Task 模型测试
# ============================================================
def test_task_creation():
    """测试任务创建"""
    task = Task(
        task_id="T-001",
        user_id="U1001",
        ticket_content="退款",
        order_id="ORD-001",
    )
    assert task.task_id == "T-001"
    assert task.status == TaskStatus.CREATED
    assert task.priority == TaskPriority.REALTIME
    assert task.retry_count == 0


def test_task_default_values():
    """测试任务默认值"""
    task = Task(
        task_id="T-002",
        user_id="U1002",
        ticket_content="测试",
    )
    assert task.max_retries == 3
    assert task.timeout_seconds == 300
    assert task.result is None


# ============================================================
# RefundEligibility 模型测试
# ============================================================
def test_refund_eligibility_eligible():
    """测试符合退款条件"""
    eligibility = RefundEligibility(
        eligible=True,
        decision_code="COURSE_SERVICE_FAILURE",
        max_refund_amount=19900,
        approval_required=False,
        evidence=["ORDER_PAID"],
    )
    assert eligibility.eligible is True
    assert eligibility.approval_required is False


def test_refund_eligibility_not_eligible():
    """测试不符合退款条件"""
    eligibility = RefundEligibility(
        eligible=False,
        decision_code="REFUND_WINDOW_EXPIRED",
        approval_required=False,
    )
    assert eligibility.eligible is False


# ============================================================
# 退款资格策略测试
# ============================================================
def test_evaluate_course_unavailable():
    """测试课程不可用退款评估"""
    result = evaluate_refund_eligibility(
        reason_code="COURSE_UNAVAILABLE",
        order_snapshot={"status": "PAID", "totalAmount": 19900},
        learning_progress={"progressPercentage": 0},
        retrieved_rules=[],
    )
    assert result.eligible is True
    assert result.decision_code == "COURSE_SERVICE_FAILURE"
    assert "ORDER_PAID" in result.evidence


def test_evaluate_duplicate_purchase():
    """测试重复购买退款评估"""
    result = evaluate_refund_eligibility(
        reason_code="DUPLICATE_PURCHASE",
        order_snapshot={"status": "PAID", "totalAmount": 9900},
        learning_progress={},
        retrieved_rules=[],
    )
    assert result.eligible is True
    assert result.decision_code == "DUPLICATE_ORDER"


def test_evaluate_expired_window():
    """测试超期退款评估"""
    result = evaluate_refund_eligibility(
        reason_code="EXPIRED_REFUND_WINDOW",
        order_snapshot={},
        learning_progress={},
        retrieved_rules=[],
    )
    assert result.eligible is False
    assert result.decision_code == "REFUND_WINDOW_EXPIRED"


def test_evaluate_no_reason_needs_approval():
    """测试无理由退款需审批"""
    result = evaluate_refund_eligibility(
        reason_code="NO_REASON",
        order_snapshot={},
        learning_progress={},
        retrieved_rules=[],
    )
    assert result.approval_required is True


def test_evaluate_exceeded_progress():
    """测试超进度退款评估"""
    result = evaluate_refund_eligibility(
        reason_code="EXCEEDED_PROGRESS_LIMIT",
        order_snapshot={},
        learning_progress={"progressPercentage": 50},
        retrieved_rules=[],
    )
    assert result.eligible is False


def test_evaluate_evidence_collection():
    """测试证据收集"""
    result = evaluate_refund_eligibility(
        reason_code="COURSE_UNAVAILABLE",
        order_snapshot={"status": "PAID", "paymentMethod": "WECHAT"},
        learning_progress={"progressPercentage": 0},
        retrieved_rules=[{"ruleId": "REFUND-001"}],
    )
    assert "ORDER_PAID" in result.evidence
    assert "PAYMENT_CONFIRMED" in result.evidence
    assert "NO_LEARNING_ACTIVITY" in result.evidence
    assert "REFUND-001" in result.rule_ids


def test_evaluate_low_progress():
    """测试低学习进度"""
    result = evaluate_refund_eligibility(
        reason_code="COURSE_UNAVAILABLE",
        order_snapshot={"status": "PAID"},
        learning_progress={"progressPercentage": 15},
        retrieved_rules=[],
    )
    assert "LOW_LEARNING_PROGRESS" in result.evidence


def test_evaluate_significant_progress():
    """测试高学习进度"""
    result = evaluate_refund_eligibility(
        reason_code="COURSE_UNAVAILABLE",
        order_snapshot={"status": "PAID"},
        learning_progress={"progressPercentage": 50},
        retrieved_rules=[],
    )
    assert "SIGNIFICANT_LEARNING_PROGRESS" in result.evidence


# ============================================================
# 异常测试
# ============================================================
def test_permission_denied_exception():
    """测试权限异常"""
    with pytest.raises(PermissionDeniedException):
        raise PermissionDeniedException("无权访问此订单")


def test_resource_not_found_exception():
    """测试资源不存在异常"""
    exc = ResourceNotFoundException("订单不存在", code="ORDER_NOT_FOUND")
    assert exc.message == "订单不存在"
    assert exc.code == "ORDER_NOT_FOUND"


def test_budget_exceeded_exception():
    """测试预算超限异常"""
    exc = BudgetExceededException("Token 超预算")
    assert exc.code == "BUDGETEXCEEDEDEXCEPTION"
