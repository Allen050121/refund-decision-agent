"""
检索 Port - 抽象接口
文档 3.3: 规则检索
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class RetrievalPort(ABC):
    """
    规则检索抽象接口
    文档 3.3: 检索流程
    """

    @abstractmethod
    async def search_rules(
        self,
        query: str,
        reason_code: Optional[str] = None,
        scenario: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        检索退款规则
        文档 3.3:
          - 元数据过滤：只保留当前生效且场景匹配的规则
          - BM25 检索
          - 返回 Top-K 规则与原文片段

        Args:
            query: 查询文本
            reason_code: 退款原因码（用于元数据过滤）
            scenario: 业务场景
            top_k: 返回结果数

        Returns:
            规则列表，每项包含:
            - ruleId: 规则 ID
            - version: 版本号
            - content: 规则内容
            - score: 相关度分数
            - scenario: 适用场景
            - riskLevel: 风险等级
            - effectiveFrom: 生效时间
            - effectiveTo: 失效时间
        """
        ...

    @abstractmethod
    async def index_rule(self, rule: Dict[str, Any]) -> None:
        """
        索引规则（管理接口）
        文档 3.3: 规则更新流程
        """
        ...
