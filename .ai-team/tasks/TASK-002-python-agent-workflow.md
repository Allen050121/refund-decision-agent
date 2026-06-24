---
title: "阶段 2: Python Agent 最小链路 - LangGraph 工作流与 Java API 集成"
task_id: "TASK-002"
status: "pending"
owner: "ai-engineer"
task_type: "implementation"
delivery_stage: "stack"
mode: "standard"
work_mode: "sequential"
workflow_mode: "standard"
created: "2026-06-24"
dependencies:
  - TASK-001
verification_status: not_run
last_run_id:
last_result:
blocked_reason:
branch:
github_issue:
github_pr:
ci_status:
tags:
  - ai-team/task
  - phase-2
  - python
  - langgraph
  - agent
---

# Task: 阶段 2 Python Agent 最小链路

## Status

- Task ID: `TASK-002`
- Owner: `ai-engineer`
- Task Type: `implementation`
- Delivery Stage: `stack`
- Status: `pending`
- Mode: `standard`
- Work Mode: `sequential`
- Workflow Mode: `standard`
- Dependencies: TASK-001 (已完成)
- Verification Status: `not_run`
- Last Run:
- Last Result:
- Blocked Reason:
- Branch:
- GitHub Issue:
- GitHub PR:
- CI Status:

## Goal

实现 Python Agent 最小链路，包含 LangGraph 工作流框架、工具定义（调用 Java API）、以及基本的退款决策流程。

## Task Layer

- Task Type: `implementation`
- Delivery Stage: `stack`
- This card is allowed to produce: LangGraph 工作流、工具定义、FastAPI 入口、配置管理
- This card must not skip: 工具权限校验、Java API 调用、错误处理
- Next expected card: `TASK-003` (RAG 规则检索)

## Product Decisions

- Audience: 一线售后客服（通过 Agent 交互）
- Primary pain: 需要自动化工具辅助退款决策，但不能完全依赖模型判断
- MVP use case: 客服输入订单 ID，Agent 调用 Java API 获取数据并给出退款建议
- Product surface: FastAPI + LangGraph + 命令行/简单 Web 界面
- Confirmed stack choices: Python 3.12, FastAPI, LangGraph, Redis Streams (后续)
- Scale/capacity assumption: MVP 单机部署，低并发

## Questions For Human Lead

1. **Agent 交互方式？** 命令行 vs Web 界面 vs API
   - 默认：先实现命令行版本，后续添加 Web 界面

2. **是否需要对话历史？** 
   - 默认：MVP 版本无对话历史，单次查询

## Non-Goals

- 不实现 RAG 规则检索（阶段 3）
- 不实现 Redis Streams 异步任务（阶段 4）
- 不实现复杂对话管理
- 不实现多轮交互

## Product Surface And UX Source

- Source screens/pages: 命令行界面
- User actions: 输入订单 ID 和退款原因
- Components involved: LangGraph 工作流、工具调用、Java API 集成
- Loading/empty/error states: 标准错误提示
- Frontend approval status: N/A（MVP 版本）

## API And Business Mapping

| Agent 工具 | Java API | 用途 | 输入 | 输出 |
|---|---|---|---|---|
| get_order | GET /api/orders/{orderId} | 查询订单信息 | orderId, requesterUserId | OrderResponse |
| get_learning_progress | GET /api/learning/{orderId} | 查询学习进度 | orderId, requesterUserId | LearningProgressResponse |
| get_course_status | GET /api/courses/{courseId}/status | 查询课程状态 | courseId | CourseStatusResponse |
| check_eligibility | POST /api/refund/check-eligibility | 检查退款资格 | RefundEligibilityRequest | RefundEligibilityResponse |

## File Boundaries

### Allowed To Modify

```
python-agent/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── agent/
│   │   ├── workflow.py      # LangGraph 工作流
│   │   ├── state.py         # Agent 状态定义
│   │   └── nodes.py         # 工作流节点
│   ├── tools/
│   │   ├── java_api.py      # Java API 调用工具
│   │   └── base.py          # 工具基类
│   └── schemas/
│       ├── request.py       # 请求模型
│       └── response.py      # 响应模型
├── tests/
│   ├── test_workflow.py     # 工作流测试
│   └── test_tools.py        # 工具测试
└── .env.example             # 环境变量模板
```

### Must Not Modify

- `java-service/` 目录下的任何文件
- `docker/` 目录下的配置
- `.ai-team/memory/` 下的项目记忆文件

## Context To Read

- `01-售后决策 Agent-MVP 产品与开发文档.md` - 核心开发文档（阶段 2 部分）
- `.ai-team/tasks/TASK-001-java-domain-model.md` - 阶段 1 任务卡
- `java-service/src/main/java/com/example/aftersale/interfaces/controller/RefundQueryController.java` - Java API 参考

## Implementation Notes

### LangGraph 工作流设计（按文档 5.2）

```
[Start] → [Parse Input] → [Call Java API] → [Analyze Data] → [Generate Response] → [End]
```

### 工具定义（按文档 5.3）

```python
@tool
def get_order(order_id: str, requester_user_id: str) -> dict:
    """查询订单信息"""
    response = requests.get(f"{JAVA_API_URL}/api/orders/{order_id}", 
                          params={"requesterUserId": requester_user_id})
    return response.json()

@tool
def get_learning_progress(order_id: str, requester_user_id: str) -> dict:
    """查询学习进度"""
    response = requests.get(f"{JAVA_API_URL}/api/learning/{order_id}", 
                          params={"requesterUserId": requester_user_id})
    return response.json()

@tool
def get_course_status(course_id: str) -> dict:
    """查询课程状态"""
    response = requests.get(f"{JAVA_API_URL}/api/courses/{course_id}/status")
    return response.json()
```

### 配置管理

```python
# .env
JAVA_API_URL=http://localhost:8080
REDIS_URL=redis://192.168.85.66:6379/0
ELASTICSEARCH_URL=http://192.168.85.66:9200
LLM_MODEL=gpt-4
```

## Acceptance Criteria

- [ ] LangGraph 工作流框架搭建完成
- [ ] 4 个 Java API 工具定义完成
- [ ] 工具调用 Java API 成功
- [ ] 错误处理完善（网络超时、API 错误）
- [ ] 命令行界面可交互
- [ ] 单元测试覆盖核心流程
- [ ] 工具权限校验通过
- [ ] 配置管理完善（.env 支持）

## Verification

```bash
# Python 单元测试
cd python-agent
pytest tests/

# 命令行测试
python -m app.main --order-id O20260622001 --user-id U1001

# 验证工具调用
python -c "from app.tools.java_api import get_order; print(get_order('O20260622001', 'U1001'))"
```

## Handoff Notes

- Changed files:
- Verification result:
- Run evidence:
- Known follow-ups: TASK-003 RAG 规则检索
- Memory updates needed:
