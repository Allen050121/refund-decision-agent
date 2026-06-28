"""
Agent 工作流状态定义
文档 5.1: 状态定义
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class IntentEnum(str, Enum):
    """意图类型"""
    REFUND_REQUEST = "REFUND_REQUEST"
    OTHER = "OTHER"


class ReasonCodeEnum(str, Enum):
    """退款原因码"""
    COURSE_UNAVAILABLE = "COURSE_UNAVAILABLE"
    DUPLICATE_PURCHASE = "DUPLICATE_PURCHASE"
    NO_REASON = "NO_REASON"
    EXCEEDED_PROGRESS_LIMIT = "EXCEEDED_PROGRESS_LIMIT"
    EXPIRED_REFUND_WINDOW = "EXPIRED_REFUND_WINDOW"
    PROMOTIONAL_RESTRICTION = "PROMOTIONAL_RESTRICTION"
    GENERAL = "GENERAL"


class DecisionEnum(str, Enum):
    """决策类型"""
    REFUND_RECOMMENDED = "REFUND_RECOMMENDED"
    REFUND_REJECTED = "REFUND_REJECTED"
    NEED_MORE_INFORMATION = "NEED_MORE_INFORMATION"
    WAIT_FOR_APPROVAL = "WAIT_FOR_APPROVAL"


class ApprovalActionEnum(str, Enum):
    """审批动作"""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MODIFY_AND_APPROVE = "MODIFY_AND_APPROVE"
    REQUEST_MORE_INFO = "REQUEST_MORE_INFO"


class AgentState(BaseModel):
    """
    LangGraph 工作流状态
    文档 5.1: 状态定义
    """

    # 任务基本信息
    task_id: Optional[str] = Field(None, description="任务 ID")
    user_id: Optional[str] = Field(None, description="用户 ID")
    ticket_content: Optional[str] = Field(None, description="工单内容")

    # 意图识别
    intent: Optional[IntentEnum] = Field(None, description="意图类型")
    reason_code: Optional[ReasonCodeEnum] = Field(None, description="退款原因码")

    # 业务数据
    order_id: Optional[str] = Field(None, description="订单 ID")
    order_snapshot: Optional[Dict[str, Any]] = Field(None, description="订单快照")
    learning_progress: Optional[Dict[str, Any]] = Field(None, description="学习进度")
    course_status: Optional[Dict[str, Any]] = Field(None, description="课程状态")

    # RAG 检索结果
    retrieved_rules: Optional[List[Dict[str, Any]]] = Field(None, description="检索到的规则")

    # 资格校验结果
    eligibility_result: Optional[Dict[str, Any]] = Field(None, description="资格校验结果")

    # 决策结果
    decision: Optional[DecisionEnum] = Field(None, description="决策类型")
    approval: Optional[ApprovalActionEnum] = Field(None, description="审批动作")

    # 错误和预算
    errors: List[str] = Field(default_factory=list, description="错误列表")
    budget: Dict[str, Any] = Field(default_factory=lambda: {
        "max_model_calls": 10,
        "max_tool_calls": 15,
        "max_token_cost": 1.0,
        "used_model_calls": 0,
        "used_tool_calls": 0,
        "used_token_cost": 0.0
    }, description="预算控制")

    # Trace 上下文
    trace_context: Optional[Dict[str, Any]] = Field(None, description="Trace 上下文")

    # 缺失字段
    missing_fields: List[str] = Field(default_factory=list, description="缺失字段")

    # 风险提示
    risk_hints: List[str] = Field(default_factory=list, description="风险列表")

    # 证据列表
    evidence: List[str] = Field(default_factory=list, description="证据列表")

    # 规则引用
    rule_citations: List[str] = Field(default_factory=list, description="规则引用")
