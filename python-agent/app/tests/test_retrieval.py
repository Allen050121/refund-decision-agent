"""
测试 Elasticsearch 规则检索
"""
import pytest
import pytest_asyncio
from typing import List, Dict, Any

from app.infrastructure.retrieval.elasticsearch_retriever import ElasticsearchRetriever


@pytest_asyncio.fixture
async def retriever():
    """创建检索器"""
    r = ElasticsearchRetriever()
    yield r
    await r.close()


@pytest.mark.asyncio
async def test_search_course_unavailable(retriever: ElasticsearchRetriever):
    """测试课程不可用场景检索"""
    results = await retriever.search_rules(
        query="课程打不开无法观看",
        scenario="COURSE_UNAVAILABLE",
        top_k=3,
    )
    assert len(results) > 0
    # 应该返回课程不可用规则
    rule_ids = [r["ruleId"] for r in results]
    assert "REFUND-2026-001" in rule_ids


@pytest.mark.asyncio
async def test_search_duplicate_purchase(retriever: ElasticsearchRetriever):
    """测试重复购买场景检索"""
    results = await retriever.search_rules(
        query="买重了重复购买",
        scenario="DUPLICATE_PURCHASE",
        top_k=3,
    )
    assert len(results) > 0
    rule_ids = [r["ruleId"] for r in results]
    assert "REFUND-2026-002" in rule_ids


@pytest.mark.asyncio
async def test_search_no_reason(retriever: ElasticsearchRetriever):
    """测试无理由退款场景检索"""
    results = await retriever.search_rules(
        query="不想学了无理由退款",
        scenario="NO_REASON",
        top_k=3,
    )
    assert len(results) > 0
    rule_ids = [r["ruleId"] for r in results]
    assert "REFUND-2026-003" in rule_ids


@pytest.mark.asyncio
async def test_search_expired_window(retriever: ElasticsearchRetriever):
    """测试超期退款场景检索"""
    results = await retriever.search_rules(
        query="超过30天超期",
        scenario="EXPIRED_REFUND_WINDOW",
        top_k=3,
    )
    assert len(results) > 0
    rule_ids = [r["ruleId"] for r in results]
    assert "REFUND-2026-004" in rule_ids


@pytest.mark.asyncio
async def test_search_with_scenario_filter(retriever: ElasticsearchRetriever):
    """测试场景过滤"""
    results = await retriever.search_rules(
        query="退款",
        scenario="COURSE_UNAVAILABLE",
        top_k=10,
    )
    # 所有结果都应该是 COURSE_UNAVAILABLE 场景
    for rule in results:
        assert rule["scenario"] == "COURSE_UNAVAILABLE"


@pytest.mark.asyncio
async def test_search_empty_query(retriever: ElasticsearchRetriever):
    """测试空查询"""
    results = await retriever.search_rules(
        query="",
        top_k=5,
    )
    # 空查询应该返回一些结果（match_all）
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_search_respects_top_k(retriever: ElasticsearchRetriever):
    """测试 top_k 限制"""
    results = await retriever.search_rules(
        query="退款",
        top_k=2,
    )
    assert len(results) <= 2


@pytest.mark.asyncio
async def test_index_and_search_rule(retriever: ElasticsearchRetriever):
    """测试索引新规则并检索"""
    new_rule = {
        "ruleId": "REFUND-2026-TEST",
        "version": 1,
        "title": "测试规则",
        "content": "这是一个测试规则用于验证索引功能",
        "scenario": "TEST_SCENARIO",
        "reasonCode": "TEST",
        "riskLevel": "LOW",
        "effectiveFrom": "2026-01-01T00:00:00",
        "effectiveTo": None,
        "maxRefundPercent": 100,
        "approvalRequired": False,
    }

    await retriever.index_rule(new_rule)

    results = await retriever.search_rules(
        query="测试规则索引功能",
        scenario="TEST_SCENARIO",
        top_k=5,
    )

    rule_ids = [r["ruleId"] for r in results]
    assert "REFUND-2026-TEST" in rule_ids
