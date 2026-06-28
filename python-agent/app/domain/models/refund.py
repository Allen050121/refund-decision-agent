"""
退款决策领域模型
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class DecisionType(str, Enum):
    """决策类型"""

    REFUND_RECOMMENDED = "REFUND_RECOMMENDED"
    REFUND_REJECTED = "REFUND_REJECTED"
    NEED_MORE_INFORMATION = "NEED_MORE_INFORMATION"
    WAIT_FOR_APPROVAL = "WAIT_FOR_APPROVAL"


class RiskLevel(str, Enum):
    """风险等级"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RefundEligibility(BaseModel):
    """退款资格校验结果"""

    eligible: bool = Field(..., description="是否符合退款条件")
    decision_code: str = Field(..., description="决策码")
    max_refund_amount: Optional[int] = Field(None, description="最大可退金额（分）")
    approval_required: bool = Field(default=False, description="是否需要审批")
    evidence: List[str] = Field(default_factory=list, description="证据列表")
    rule_ids: List[str] = Field(default_factory=list, description="引用的规则 ID")


class RefundDecision(BaseModel):
    """退款决策结果"""

    task_id: str = Field(..., description="任务 ID")
    decision: DecisionType = Field(..., description="决策类型")
    reason_code: Optional[str] = Field(None, description="退款原因码")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="风险等级")

    # 金额
    recommended_amount: Optional[int] = Field(None, description="建议退款金额（分）")
    max_allowed_amount: Optional[int] = Field(None, description="最大允许金额（分）")

    # 引用
    rule_citations: List[str] = Field(default_factory=list, description="规则引用")
    evidence: List[str] = Field(default_factory=list, description="证据列表")
    risk_hints: List[str] = Field(default_factory=list, description="风险提示")

    # Trace
    model_calls: int = Field(default=0, description="模型调用次数")
    tool_calls: int = Field(default=0, description="工具调用次数")
    total_tokens: int = Field(default=0, description="总 Token 消耗")
    estimated_cost: float = Field(default=0.0, description="预估成本（美元）")

    # 时间
    decided_at: datetime = Field(default_factory=datetime.utcnow)
