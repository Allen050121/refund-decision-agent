"""
检索召回率评测脚本
计算 Recall@K, Precision@K, MRR 等指标
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from app.infrastructure.retrieval.elasticsearch_retriever import ElasticsearchRetriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_metrics(
    test_cases: List[Dict[str, Any]],
    results: List[List[Dict[str, Any]]],
    k: int = 3,
) -> Dict[str, float]:
    """计算召回率指标"""
    recalls = []
    precisions = []
    mrrs = []
    no_hits = []

    for test_case, result in zip(test_cases, results):
        expected = set(test_case["expected_rules"])
        retrieved = set(r["ruleId"] for r in result[:k])

        # Recall@K
        if expected:
            recall = len(expected & retrieved) / len(expected)
            recalls.append(recall)

        # Precision@K
        if retrieved:
            precision = len(expected & retrieved) / len(retrieved)
            precisions.append(precision)

        # MRR (Mean Reciprocal Rank)
        for i, rule in enumerate(result[:k]):
            if rule["ruleId"] in expected:
                mrrs.append(1.0 / (i + 1))
                break
        else:
            mrrs.append(0.0)

        # No-hit accuracy (无适用规则时是否正确不召回)
        if not expected and not retrieved:
            no_hits.append(1.0)
        elif not expected:
            no_hits.append(0.0)

    return {
        "Recall@3": sum(recalls) / len(recalls) if recalls else 0.0,
        "Precision@3": sum(precisions) / len(precisions) if precisions else 0.0,
        "MRR": sum(mrrs) / len(mrrs) if mrrs else 0.0,
        "No-hit Accuracy": sum(no_hits) / len(no_hits) if no_hits else 1.0,
        "Total Tests": len(test_cases),
    }


async def main():
    """主函数"""
    retriever = ElasticsearchRetriever()

    # 加载测试集
    test_file = Path(__file__).parent.parent.parent / "data" / "test_queries.json"
    with open(test_file, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    logger.info(f"加载测试集：{len(test_cases)} 个测试用例")

    # 执行检索
    results = []
    for test_case in test_cases:
        result = await retriever.search_rules(
            query=test_case["query"],
            scenario=test_case.get("scenario"),
            top_k=5,
        )
        results.append(result)

    # 计算指标
    metrics = calculate_metrics(test_cases, results, k=3)

    logger.info("=" * 60)
    logger.info("检索评测结果")
    logger.info("=" * 60)
    for metric, value in metrics.items():
        if isinstance(value, float):
            logger.info(f"  {metric}: {value:.3f}")
        else:
            logger.info(f"  {metric}: {value}")
    logger.info("=" * 60)

    # 详细结果
    logger.info("\n详细结果：")
    for i, (test_case, result) in enumerate(zip(test_cases, results)):
        expected = set(test_case["expected_rules"])
        retrieved = set(r["ruleId"] for r in result[:3])
        hit = expected & retrieved
        status = "HIT" if hit else "MISS"
        logger.info(
            f"  [{status}] {test_case['query'][:20]:<20} | "
            f"expected={expected} | retrieved={retrieved}"
        )

    await retriever.close()


if __name__ == "__main__":
    asyncio.run(main())
