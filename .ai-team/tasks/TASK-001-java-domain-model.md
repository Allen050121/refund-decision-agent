---
title: "阶段1: Java确定性业务底座 - 领域模型与退款资格校验"
task_id: "TASK-001"
status: "pending"
owner: "backend-engineer"
task_type: "implementation"
delivery_stage: "stack"
mode: "standard"
work_mode: "sequential"
workflow_mode: "standard"
created: "2026-06-23"
dependencies:
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
  - phase-1
  - java
  - domain-model
---

# Task: 阶段1 Java确定性业务底座

## Status

- Task ID: `TASK-001`
- Owner: `backend-engineer`
- Task Type: `implementation`
- Delivery Stage: `stack`
- Status: `pending`
- Mode: `standard`
- Work Mode: `sequential`
- Workflow Mode: `standard`
- Dependencies: 无
- Verification Status: `not_run`
- Last Run:
- Last Result:
- Blocked Reason:
- Branch:
- GitHub Issue:
- GitHub PR:
- CI Status:

## Goal

实现 Java 确定性业务底座，包含领域模型和退款资格校验服务，使退款决策能由确定性业务规则计算而非依赖模型判断。

## Task Layer

- Task Type: `implementation`
- Delivery Stage: `stack`
- This card is allowed to produce: 领域模型、业务服务、单元测试
- This card must not skip: 权限校验、退款资格计算
- Next expected card: `TASK-002` (Python Agent 最小链路)

## Product Decisions

- Audience: 一线售后客服、售后主管
- Primary pain: 退款决策需要确定性规则校验，不能依赖模型判断金额和资格
- MVP use case: 6类退款场景的资格校验（重复购买、课程无法观看、无理由退款、超出学习限制、超过有效期、订单不存在）
- Product surface: Java REST API (内部服务，供 Python Agent 调用)
- Confirmed stack choices: Java 21, Spring Boot 3, Spring Data JPA, MySQL 8, Flyway
- Scale/capacity assumption: MVP 单机部署，低并发
- Human Lead approvals needed: 领域模型设计确认

## Questions For Human Lead

1. **数据库是否已创建？** 需要在虚拟机 MySQL 执行 SQL 文件
   - 默认: 等待确认后再继续实现

2. **领域模型是否按文档 4.3 结构实现？**
   - 默认: 是，按文档定义的 DDD 结构实现

## Non-Goals

- 不实现前端界面（阶段 6）
- 不实现 Python Agent（阶段 2）
- 不实现 RAG 检索（阶段 3）
- 不实现 Redis Streams（阶段 4）
- 不由模型判断退款金额（硬边界）

## Product Surface And UX Source

- Source screens/pages: 无（内部 API）
- User actions: Python Agent 调用 Java API
- Components involved: 订单查询、学习进度查询、退款资格校验
- Loading/empty/error states: 标准错误响应（RESOURCE_NOT_FOUND, PERMISSION_DENIED, VALIDATION_ERROR, DEPENDENCY_TIMEOUT）
- Frontend approval status: N/A（后端服务）

## API And Business Mapping

| Endpoint/Action | Source UI or Trigger | Business Rule | Auth/Permission | Error States |
|---|---|---|---|---|
| GET /api/orders/{orderId} | Python Agent 工具调用 | 订单归属校验 | 验证 requesterUserId | PERMISSION_DENIED |
| GET /api/learning/{orderId} | Python Agent 工具调用 | 学习进度查询 | 订单归属校验 | RESOURCE_NOT_FOUND |
| POST /api/refund/check-eligibility | Python Agent 工具调用 | 退款资格计算 | 订单归属校验 | VALIDATION_ERROR |
| GET /api/courses/{courseId}/status | Python Agent 工具调用 | 课程状态查询 | 无 | RESOURCE_NOT_FOUND |

## File Boundaries

### Allowed To Modify

```
java-service/src/main/java/com/example/aftersale/
├── domain/
│   ├── support/          # 工单领域
│   │   └── SupportTicket.java
│   ├── refund/           # 退款领域
│   │   ├── RefundRequest.java
│   │   └── RefundEligibilityService.java
│   ├── agenttask/        # Agent任务领域
│   │   └── AgentTask.java
│   └── shared/           # 共享值对象
│   │   ├── OrderId.java
│   │   ├── UserId.java
│   │   ├── Money.java
│   │   └── RuleVersion.java
├── application/
│   ├── service/
│   │   ├── OrderQueryService.java
│   │   ├── LearningProgressService.java
│   │   ├── RefundEligibilityService.java
│   ├── port/
│   │   ├── OrderRepository.java
│   │   ├── LearningProgressRepository.java
├── infrastructure/
│   ├── persistence/
│   │   ├── OrderJpaRepository.java
│   │   ├── LearningProgressJpaRepository.java
├── interfaces/
│   ├── controller/
│   │   ├── OrderController.java
│   │   ├── LearningController.java
│   │   ├── RefundController.java
│   │   ├── CourseController.java
│   ├── dto/
│   │   ├── OrderResponse.java
│   │   ├── LearningProgressResponse.java
│   │   ├── RefundEligibilityRequest.java
│   │   ├── RefundEligibilityResponse.java
```

### Must Not Modify

- `python-agent/` 目录下的任何文件
- `docker/` 目录下的配置
- `docs/` 目录下的文档
- `.ai-team/memory/` 下的项目记忆文件
- 数据库迁移脚本除非显式更新此卡

## Context To Read

- `01-售后决策Agent-MVP产品与开发文档.md` - 核心开发文档
- `.ai-team/memory/project-brief.md` - 项目简介
- `.ai-team/memory/technology-policy.md` - 技术策略
- `.ai-team/memory/pitfalls.md` - 避坑指南

## Implementation Notes

### 退款资格校验规则（按文档 3.4）

输入：
```json
{
  "orderId": "O20260622001",
  "requesterUserId": "U1001",
  "reasonCode": "COURSE_UNAVAILABLE",
  "ruleVersion": 3
}
```

输出：
```json
{
  "eligible": true,
  "decisionCode": "COURSE_SERVICE_FAILURE",
  "maxRefundAmount": 19900,
  "approvalRequired": false,
  "evidence": ["ORDER_PAID", "COURSE_UNAVAILABLE", "WITHIN_REFUND_WINDOW"]
}
```

### 关键边界（按文档要求）

1. **金额使用整数分**，禁止浮点数
2. **校验订单归属**，不信任 Python 传入的结论
3. **Agent 只能获取建议上限**，不能自行决定最终退款金额
4. **写操作必须由 Java 在人工确认后执行**

### 标准错误码

- `RESOURCE_NOT_FOUND` - 订单不存在
- `PERMISSION_DENIED` - 订单不属于当前用户
- `VALIDATION_ERROR` - 参数错误
- `DEPENDENCY_TIMEOUT` - 依赖服务超时
- `DEPENDENCY_UNAVAILABLE` - 依赖服务不可用

## Acceptance Criteria

- [ ] 领域模型按文档结构实现
- [ ] 值对象 Money 使用整数分
- [ ] 退款资格校验服务实现确定性规则
- [ ] 订单归属校验实现
- [ ] 标准错误码返回
- [ ] 单元测试覆盖核心规则
- [ ] 退款资格规则测试全部通过
- [ ] 重复请求不会产生重复业务结果（幂等）
- [ ] 工具权限与参数校验通过

## Verification

```powershell
# Java 单元测试
cd java-service
mvn test

# 验证服务启动
curl http://localhost:8080/health
```

## Handoff Notes

- Changed files:
- Verification result:
- Run evidence:
- Known follow-ups: TASK-002 Python Agent 最小链路
- Memory updates needed: