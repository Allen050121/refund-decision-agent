---
title: "阶段 3: RAG 规则检索 - Elasticsearch BM25 与元数据过滤"
task_id: "TASK-003"
status: "completed"
owner: "ai-engineer"
task_type: "implementation"
delivery_stage: "stack"
mode: "standard"
work_mode: "sequential"
workflow_mode: "standard"
created: "2026-06-25"
dependencies:
  - TASK-002
verification_status: passed
last_run_id:
last_result: "recall@3=1.0,all_tests_passed"
blocked_reason:
branch: "master"
github_issue:
github_pr:
ci_status:
tags:
  - ai-team/task
  - phase-3
  - rag
  - elasticsearch
  - retrieval
---

# Task: 阶段 3 RAG 规则检索

## Status

- Task ID: `TASK-003`
- Owner: `ai-engineer`
- Task Type: `implementation`
- Delivery Stage: `stack`
- Status: `pending`
- Mode: `standard`
- Work Mode: `sequential`
- Workflow Mode: `standard`
- Dependencies: TASK-002 (已完成)
- Verification Status: `not_run`
- Last Run:
- Last Result:
- Blocked Reason:
- Branch:
- GitHub Issue:
- GitHub PR:
- CI Status:

## Goal

实现退款规则的 RAG 检索能力，使用 Elasticsearch BM25 进行基线检索，支持元数据过滤和规则冲突检测。

## Task Layer

- Task Type: `implementation`
- Delivery Stage: `stack`
- This card is allowed to produce: ES 索引设计、检索服务、评测脚本、规则数据
- This card must not skip: 元数据过滤、冲突检测、版本控制、召回率评测
- Next expected card: `TASK-004` (向量检索与 Hybrid Search)

## Product Decisions

- Audience: 一线售后客服（通过 Agent 交互）
- Primary pain: 退款规则持续更新，需要动态检索而非固化在 Prompt 中
- MVP use case: 根据工单内容检索适用的退款规则，返回规则 ID、版本和原文
- Product surface: Elasticsearch BM25 + 元数据过滤
- Confirmed stack choices: Elasticsearch, BM25, Python
- Scale/capacity assumption: MVP 规则数量 < 100 条，单索引

## Questions For Human Lead

1. **是否需要向量检索？**
   - 默认：先完成 BM25 基线，评测后再决定是否增加向量检索

2. **规则数据从哪来？**
   - 默认：手动构造标准规则集用于 MVP

## Non-Goals

- 不实现向量检索（阶段 4）
- 不实现 Rerank 模型
- 不实现复杂 Hybrid Search
- 不实现规则自动同步流程
- 不实现多语言规则

## Product Surface And UX Source

- Source screens/pages: Agent 内部调用
- User actions: 输入工单内容，Agent 自动检索相关规则
- Components involved: Elasticsearch, BM25, 元数据过滤
- Loading/empty/error states: 无适用规则时返回空列表

## API And Business Mapping

| 功能 | 输入 | 输出 |
|------|------|------|
| 规则检索 | query, scenario, top_k | List[Rule] |
| 规则索引 | rule_document | rule_id |
| 冲突检测 | rules | bool |

## File Boundaries

### Allowed To Modify

```
python-agent/
├── app/
│   ├── infrastructure/
│   │   └── retrieval/
│   │       ├── elasticsearch_retriever.py   # ES 检索实现
│   │       ├── fake_retriever.py            # 假实现（测试用）
│   │       └── rule_indexer.py              # 规则索引管理（新增）
│   └── tests/
│       └── test_retrieval.py                # 检索测试（新增）
└── data/
    └── refund_rules.json                    # 规则数据（新增）
```

### Must Not Modify

- `java-service/` 目录下的任何文件
- `app/domain/` 下的领域模型
- `app/application/ports/` 下的接口定义

## Context To Read

- `01-售后决策 Agent-MVP 产品与开发文档.md` - 文档 3.3 RAG 规则检索
- `.ai-team/tasks/TASK-002-python-agent-workflow.md` - 阶段 2 任务卡
- `python-agent/app/infrastructure/retrieval/elasticsearch_retriever.py` - 现有 ES 检索实现

## Implementation Notes

### ES 索引设计

```json
{
  "mappings": {
    "properties": {
      "ruleId": { "type": "keyword" },
      "version": { "type": "integer" },
      "scenario": { "type": "keyword" },
      "content": { "type": "text", "analyzer": "standard" },
      "effectiveFrom": { "type": "date" },
      "effectiveTo": { "type": "date", "null_value": "9999-12-31" },
      "riskLevel": { "type": "keyword" },
      "contentHash": { "type": "keyword" }
    }
  }
}
```

### 检索流程

```python
async def search_rules(query: str, scenario: str, top_k: int = 5) -> List[Rule]:
    # 1. 元数据过滤
    filter = {
        "bool": {
            "must": [
                {"term": {"scenario": scenario}} if scenario else None,
                {"range": {"effectiveFrom": {"lte": "now"}}},
                {"range": {"effectiveTo": {"gte": "now"}}}
            ]
        }
    }
    
    # 2. BM25 检索
    query = {
        "match": {"content": query}
    }
    
    # 3. 返回 Top-K
    response = await es.search(index="refund-rules", query=query, filter=filter, size=top_k)
    return parse_rules(response)
```

### 规则冲突检测

```python
def has_conflict(rules: List[Rule]) -> bool:
    # 同一场景有多条规则且建议不同决策 → 冲突
    scenarios = {}
    for rule in rules:
        if rule.scenario in scenarios:
            return True
        scenarios[rule.scenario] = rule
    return False
```

## Acceptance Criteria

- [ ] ES 索引创建成功
- [ ] 规则数据导入成功（至少 10 条标准规则）
- [ ] BM25 检索返回正确规则
- [ ] 元数据过滤（生效时间、场景）工作正常
- [ ] 冲突检测逻辑正确
- [ ] 召回率测试通过（Recall@3 >= 0.8）
- [ ] 单元测试覆盖核心检索逻辑
- [ ] FakeRetriever 与真实实现接口一致

## Verification

```bash
# 启动 ES（如果未运行）
docker run -d -p 9200:9200 elasticsearch:8.11.0

# 导入规则数据
python -m app.infrastructure.retrieval.rule_indexer --import data/refund_rules.json

# 运行检索测试
cd python-agent
pytest app/tests/test_retrieval.py -v

# 召回率评测
python -m app.tests.retrieval_eval --test-set data/test_queries.json
```

## Handoff Notes

- Changed files:
- Verification result:
- Run evidence:
- Known follow-ups: TASK-004 向量检索与 Hybrid Search
- Memory updates needed:
