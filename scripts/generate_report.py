"""
生成评测报告
一条命令执行完整评测并生成报告
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "python-agent"))

from app.infrastructure.retrieval.elasticsearch_retriever import ElasticsearchRetriever


def load_test_set() -> list:
    """加载测试集"""
    test_file = Path(__file__).parent.parent / "python-agent" / "data" / "test_queries.json"
    with open(test_file, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_metrics(test_cases: list, results: list, k: int = 3) -> dict:
    """计算召回率指标"""
    recalls = []
    precisions = []
    mrrs = []

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

        # MRR
        for i, rule in enumerate(result[:k]):
            if rule["ruleId"] in expected:
                mrrs.append(1.0 / (i + 1))
                break
        else:
            mrrs.append(0.0)

    return {
        "Recall@3": sum(recalls) / len(recalls) if recalls else 0.0,
        "Precision@3": sum(precisions) / len(precisions) if precisions else 0.0,
        "MRR": sum(mrrs) / len(mrrs) if mrrs else 0.0,
        "Total Tests": len(test_cases),
        "Passed": sum(1 for tc, r in zip(test_cases, results) if set(tc["expected_rules"]) & set(x["ruleId"] for x in r[:k])),
        "Failed": sum(1 for tc, r in zip(test_cases, results) if not (set(tc["expected_rules"]) & set(x["ruleId"] for x in r[:k]))),
    }


async def run_evaluation():
    """运行评测"""
    print("=" * 60)
    print("  售后退款决策 Agent - 评测报告")
    print("=" * 60)
    print()

    # 加载测试集
    test_cases = load_test_set()
    print(f"加载测试集：{len(test_cases)} 条")

    # 初始化检索器
    retriever = ElasticsearchRetriever()

    # 执行检索
    results = []
    for i, test_case in enumerate(test_cases):
        result = await retriever.search_rules(
            query=test_case["query"],
            scenario=test_case.get("scenario"),
            top_k=5,
        )
        results.append(result)
        if (i + 1) % 20 == 0:
            print(f"  进度：{i + 1}/{len(test_cases)}")

    # 计算指标
    metrics = calculate_metrics(test_cases, results, k=3)

    print()
    print("=" * 60)
    print("  总体指标")
    print("=" * 60)
    for metric, value in metrics.items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.3f}")
        else:
            print(f"  {metric}: {value}")

    print()
    print("=" * 60)
    print("  各场景通过率")
    print("=" * 60)

    scenario_stats = {}
    for test_case, result in zip(test_cases, results):
        scenario = test_case.get("scenario") or "UNKNOWN"
        if scenario not in scenario_stats:
            scenario_stats[scenario] = {"total": 0, "passed": 0}
        scenario_stats[scenario]["total"] += 1

        expected = set(test_case["expected_rules"])
        retrieved = set(r["ruleId"] for r in result[:3])
        if expected & retrieved:
            scenario_stats[scenario]["passed"] += 1

    for scenario, stats in sorted(scenario_stats.items()):
        rate = stats["passed"] / stats["total"] if stats["total"] > 0 else 0
        print(f"  {scenario}: {stats['passed']}/{stats['total']} = {rate:.1%}")

    print()
    print("=" * 60)
    print("  生成时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    await retriever.close()

    return metrics


def main():
    """主函数"""
    asyncio.run(run_evaluation())


if __name__ == "__main__":
    main()
