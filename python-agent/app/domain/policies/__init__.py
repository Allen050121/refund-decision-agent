"""
退款资格策略
"""
from typing import Dict, Any, List
from app.domain.models.refund import RefundEligibility, DecisionType


def evaluate_refund_eligibility(
    reason_code: str,
    order_snapshot: Dict[str, Any],
    learning_progress: Dict[str, Any],
    retrieved_rules: List[Dict[str, Any]],
    course_status: Dict[str, Any] = None,
) -> RefundEligibility:
    """
    评估退款资格
    综合订单数据、学习进度、课程状态和检索到的规则进行判定
    """
    evidence: List[str] = []
    rule_ids: List[str] = []

    # 提取规则引用
    for rule in retrieved_rules:
        rule_id = rule.get("ruleId", "")
        if rule_id:
            rule_ids.append(rule_id)

    # 基础证据收集
    if order_snapshot:
        if order_snapshot.get("status") == "PAID":
            evidence.append("ORDER_PAID")
        if order_snapshot.get("paymentMethod"):
            evidence.append("PAYMENT_CONFIRMED")

    if learning_progress:
        progress_pct = learning_progress.get("progressPercentage", 0)
        if progress_pct == 0:
            evidence.append("NO_LEARNING_ACTIVITY")
        elif progress_pct <= 30:
            evidence.append("LOW_LEARNING_PROGRESS")
        else:
            evidence.append("SIGNIFICANT_LEARNING_PROGRESS")

    if course_status:
        if course_status.get("isPromotional"):
            evidence.append("PROMOTIONAL_COURSE")
        if course_status.get("status") == "UNAVAILABLE":
            evidence.append("COURSE_UNAVAILABLE")

    # ============================================================
    # 关键：先检查订单状态，再根据业务数据判断
    # ============================================================

    # 检查订单是否已退款
    if order_snapshot and order_snapshot.get("hasRefunded"):
        return RefundEligibility(
            eligible=False,
            decision_code="ALREADY_REFUNDED",
            max_refund_amount=0,
            approval_required=False,
            evidence=evidence + ["ALREADY_REFUNDED"],
            rule_ids=rule_ids,
        )

    # 检查订单是否未支付
    if order_snapshot and order_snapshot.get("status") != "PAID":
        return RefundEligibility(
            eligible=False,
            decision_code="ORDER_NOT_PAID",
            max_refund_amount=0,
            approval_required=False,
            evidence=evidence + ["ORDER_NOT_PAID"],
            rule_ids=rule_ids,
        )

    # 检查课程是否促销（需审批）
    if course_status and course_status.get("isPromotional"):
        return RefundEligibility(
            eligible=True,
            decision_code="PROMOTIONAL_COURSE_RESTRICTION",
            max_refund_amount=order_snapshot.get("maxRefundAmount", 0) if order_snapshot else None,
            approval_required=True,  # 促销课程需审批
            evidence=evidence + ["PROMOTIONAL_COURSE"],
            rule_ids=rule_ids,
        )

    # 检查学习进度是否超限
    if learning_progress:
        exceeds_limit = learning_progress.get("exceedsLimit", False)
        progress_pct = learning_progress.get("progressPercentage", 0)

        if exceeds_limit or progress_pct > 30:
            return RefundEligibility(
                eligible=False,
                decision_code="PROGRESS_LIMIT_EXCEEDED",
                max_refund_amount=0,
                approval_required=False,
                evidence=evidence + ["PROGRESS_EXCEEDS_30_PERCENT"],
                rule_ids=rule_ids,
            )

    # ============================================================
    # 根据原因码判断
    # ============================================================
    eligible = True
    decision_code = "MANUAL_REVIEW"
    approval_required = False
    max_refund_amount = None

    if "COURSE_UNAVAILABLE" == reason_code:
        decision_code = "COURSE_SERVICE_FAILURE"
        max_refund_amount = order_snapshot.get("maxRefundAmount", 0) if order_snapshot else None
        eligible = True
    elif "DUPLICATE_PURCHASE" == reason_code:
        decision_code = "DUPLICATE_ORDER"
        max_refund_amount = order_snapshot.get("maxRefundAmount", 0) if order_snapshot else None
        eligible = True
    elif "EXCEEDED_PROGRESS_LIMIT" == reason_code:
        decision_code = "PROGRESS_LIMIT_EXCEEDED"
        eligible = False
    elif "EXPIRED_REFUND_WINDOW" == reason_code:
        decision_code = "REFUND_WINDOW_EXPIRED"
        eligible = False
    elif "NO_REASON" == reason_code:
        decision_code = "NO_REASON_REQUEST"
        approval_required = True  # 无理由退款需审批
    elif "PROMOTIONAL_RESTRICTION" == reason_code:
        decision_code = "PROMOTIONAL_COURSE_RESTRICTION"
        approval_required = True  # 促销课程需审批

    return RefundEligibility(
        eligible=eligible,
        decision_code=decision_code,
        max_refund_amount=max_refund_amount,
        approval_required=approval_required,
        evidence=evidence,
        rule_ids=rule_ids,
    )
