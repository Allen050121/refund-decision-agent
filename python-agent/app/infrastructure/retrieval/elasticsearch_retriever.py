"""
Elasticsearch 规则检索实现
文档 3.3: 检索流程
  - 元数据过滤：只保留当前生效且场景匹配的规则
  - BM25 检索
  - 可选 dense vector 检索
  - 返回 Top-K 规则与原文片段
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from elasticsearch import AsyncElasticsearch

from app.application.ports.retrieval_port import RetrievalPort
from app.config import settings

logger = logging.getLogger(__name__)


class ElasticsearchRetriever(RetrievalPort):
    """
    Elasticsearch 规则检索器
    文档 3.3: MVP 首选 BM25 基线
    """

    def __init__(
        self,
        url: Optional[str] = None,
        index_name: Optional[str] = None,
    ):
        self.url = url or settings.ELASTICSEARCH_URL
        self.index_name = index_name or settings.ELASTICSEARCH_INDEX
        self._client: Optional[AsyncElasticsearch] = None

    async def _get_client(self) -> AsyncElasticsearch:
        """懒初始化 ES 客户端"""
        if self._client is None:
            self._client = AsyncElasticsearch(hosts=[self.url])
        return self._client

    async def search_rules(
        self,
        query: str,
        reason_code: Optional[str] = None,
        scenario: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        检索规则
        文档 3.3:
          1. 元数据过滤：只保留当前生效且场景匹配的规则
          2. BM25 检索
          3. 返回 Top-K 规则与原文片段
        """
        client = await self._get_client()

        # 构建查询
        must_clauses: List[Dict[str, Any]] = []
        filter_clauses: List[Dict[str, Any]] = []

        # BM25 文本检索
        if query:
            must_clauses.append({
                "multi_match": {
                    "query": query,
                    "fields": ["content", "title", "scenario"],
                    "type": "best_fields",
                }
            })

        # 文档 3.3: 元数据过滤 - 场景匹配（使用 keyword 子字段）
        if scenario:
            filter_clauses.append({"term": {"scenario.keyword": scenario}})

        if reason_code:
            filter_clauses.append({"term": {"reasonCode.keyword": reason_code}})

        # 文档 3.3: 只保留当前生效的规则
        now = datetime.utcnow().isoformat()
        filter_clauses.append({
            "bool": {
                "should": [
                    {"range": {"effectiveFrom": {"lte": now}}},
                    {"bool": {"must_not": [{"exists": {"field": "effectiveFrom"}}]}},
                ],
                "minimum_should_match": 1,
            }
        })
        filter_clauses.append({
            "bool": {
                "should": [
                    {"range": {"effectiveTo": {"gte": now}}},
                    {"bool": {"must_not": [{"exists": {"field": "effectiveTo"}}]}},
                ],
                "minimum_should_match": 1,
            }
        })

        body: Dict[str, Any] = {
            "size": top_k,
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "filter": filter_clauses,
                }
            },
            "_source": ["ruleId", "version", "content", "scenario", "riskLevel",
                        "effectiveFrom", "effectiveTo", "reasonCode"],
        }

        logger.info(f"检索规则 | query='{query[:50]}...' | scenario={scenario} | top_k={top_k}")

        try:
            response = await client.search(index=self.index_name, body=body)
            hits = response["hits"]["hits"]

            results = []
            for hit in hits:
                source = hit["_source"]
                results.append({
                    "ruleId": source.get("ruleId"),
                    "version": source.get("version"),
                    "content": source.get("content"),
                    "score": hit["_score"],
                    "scenario": source.get("scenario"),
                    "riskLevel": source.get("riskLevel"),
                    "effectiveFrom": source.get("effectiveFrom"),
                    "effectiveTo": source.get("effectiveTo"),
                    "reasonCode": source.get("reasonCode"),
                })

            logger.info(f"检索到 {len(results)} 条规则")
            return results

        except Exception as e:
            logger.error(f"规则检索失败: {e}")
            return []

    async def index_rule(self, rule: Dict[str, Any]) -> None:
        """
        索引规则
        文档 3.3: 规则更新流程
        """
        client = await self._get_client()

        doc_id = f"{rule.get('ruleId', '')}_v{rule.get('version', 1)}"

        await client.index(
            index=self.index_name,
            id=doc_id,
            body=rule,
        )
        logger.info(f"规则已索引 | ruleId={rule.get('ruleId')} | version={rule.get('version')}")

    async def close(self) -> None:
        """关闭 ES 客户端"""
        if self._client:
            await self._client.close()
            self._client = None
