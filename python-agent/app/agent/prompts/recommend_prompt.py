"""
决策建议生成 Prompt
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RecommendOutput(BaseModel):
    """决策建议结构化输出"""

    decision: str = Field(
        ...,
        description="决策: REFUND_RECOMMENDED, REFUND_REJECTED, NEED_MORE_INFORMATION, WAIT_FOR_APPROVAL",
    )
    reason: str = Field(..., description="决策理由")
    recommended_amount: Optional[int] = Field(None, description="建议退款金额（分）")
    risk_hints: List[str] = Field(default_factory=list, description="风险提示")
    rule_citations: List[str] = Field(default_factory=list, description="引用的规则 ID")


RECOMMEND_SYSTEM_PROMPT = """你是一个在线教育平台的退款决策助手。基于以下信息给出退款建议：

**输入信息**:
- 意图和退款原因
- 订单快照（状态、金额、购买时间等）
- 学习进度
- 检索到的退款规则

**决策选项**:
- REFUND_RECOMMENDED: 符合退款条件，建议退款
- REFUND_REJECTED: 不符合退款条件，拒绝退款
- NEED_MORE_INFORMATION: 信息不足，需要补充
- WAIT_FOR_APPROVAL: 需要人工审批

**决策原则**:
1. 严格依据检索到的规则做出判断
2. 必须引用具体的规则 ID
3. 如果规则冲突或不确定，标记为 WAIT_FOR_APPROVAL
4. 不要编造不存在的规则
5. 风险提示应包括：金额异常、频率异常、规则边界情况等

请严格按 JSON 格式输出。"""


def recommend_messages(
    intent: str,
    reason_code: str,
    order_snapshot: Optional[Dict[str, Any]],
    learning_progress: Optional[Dict[str, Any]],
    retrieved_rules: Optional[List[Dict[str, Any]]],
) -> List[Dict[str, str]]:
    """构建决策建议的消息列表"""

    import json

    user_content_parts = [f"## 意图和原因\n- 意图: {intent}\n- 原因码: {reason_code}"]

    if order_snapshot:
        user_content_parts.append(f"\n## 订单信息\n{json.dumps(order_snapshot, ensure_ascii=False, indent=2)}")

    if learning_progress:
        user_content_parts.append(f"\n## 学习进度\n{json.dumps(learning_progress, ensure_ascii=False, indent=2)}")

    if retrieved_rules:
        rules_text = "\n".join(
            f"- [{r.get('ruleId', '?')}] {r.get('content', '')} (场景: {r.get('scenario', '?')}, 风险: {r.get('riskLevel', '?')})"
            for r in retrieved_rules
        )
        user_content_parts.append(f"\n## 适用规则\n{rules_text}")

    return [
        {"role": "system", "content": RECOMMEND_SYSTEM_PROMPT},
        {"role": "user", "content": "\n".join(user_content_parts)},
    ]
