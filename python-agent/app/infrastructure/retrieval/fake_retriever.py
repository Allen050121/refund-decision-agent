"""
Fake 检索器 - 用于确定性测试
文档 4.4: 方便替换 Fake 实现完成确定性测试
"""
from typing import List, Dict, Any, Optional

from app.application.ports.retrieval_port import RetrievalPort


class FakeRetriever(RetrievalPort):
    """
    Fake 规则检索器
    返回预定义的规则，用于单元测试
    """

    def __init__(self, rules: Optional[List[Dict[str, Any]]] = None):
        self._rules = rules or self._default_rules()
        self.search_history: List[Dict[str, Any]] = []

    async def search_rules(
        self,
        query: str,
        reason_code: Optional[str] = None,
        scenario: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """返回预定义的规则"""
        self.search_history.append({
            "query": query,
            "reason_code": reason_code,
            "scenario": scenario,
            "top_k": top_k,
        })

        results = self._rules.copy()

        # 按场景过滤
        if scenario:
            results = [r for r in results if r.get("scenario") == scenario]

        # 按原因码过滤
        if reason_code:
            results = [r for r in results if r.get("reasonCode") == reason_code]

        return results[:top_k]

    async def index_rule(self, rule: Dict[str, Any]) -> None:
        """记录索引操作"""
        self._rules.append(rule)

    def _default_rules(self) -> List[Dict[str, Any]]:
        """默认测试规则"""
        return [
            {
                "ruleId": "REFUND-2026-001",
                "version": 1,
                "content": "课程无法观看（服务故障），全额退款",
                "score": 1.0,
                "scenario": "COURSE_UNAVAILABLE",
                "riskLevel": "LOW",
                "effectiveFrom": "2026-01-01T00:00:00",
                "effectiveTo": None,
                "reasonCode": "COURSE_UNAVAILABLE",
            },
            {
                "ruleId": "REFUND-2026-002",
                "version": 1,
                "content": "重复购买相同课程，全额退款",
                "score": 1.0,
                "scenario": "DUPLICATE_PURCHASE",
                "riskLevel": "LOW",
                "effectiveFrom": "2026-01-01T00:00:00",
                "effectiveTo": None,
                "reasonCode": "DUPLICATE_PURCHASE",
            },
            {
                "ruleId": "REFUND-2026-003",
                "version": 3,
                "content": "学习进度超过30%不支持退款",
                "score": 1.0,
                "scenario": "EXCEEDED_PROGRESS_LIMIT",
                "riskLevel": "MEDIUM",
                "effectiveFrom": "2026-06-01T00:00:00",
                "effectiveTo": None,
                "reasonCode": "EXCEEDED_PROGRESS_LIMIT",
            },
            {
                "ruleId": "REFUND-2026-004",
                "version": 1,
                "content": "超过7天退款窗口不支持退款",
                "score": 1.0,
                "scenario": "EXPIRED_REFUND_WINDOW",
                "riskLevel": "LOW",
                "effectiveFrom": "2026-01-01T00:00:00",
                "effectiveTo": None,
                "reasonCode": "EXPIRED_REFUND_WINDOW",
            },
            {
                "ruleId": "REFUND-2026-005",
                "version": 2,
                "content": "无理由退款需主管审批",
                "score": 1.0,
                "scenario": "NO_REASON",
                "riskLevel": "HIGH",
                "effectiveFrom": "2026-01-01T00:00:00",
                "effectiveTo": None,
                "reasonCode": "NO_REASON",
            },
        ]
