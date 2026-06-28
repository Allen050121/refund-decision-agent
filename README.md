# 售后退款决策 Agent

> 面向在线教育场景的售后退款决策 Agent | RAG + Tool Calling + Human-in-the-loop

[![Tests](https://img.shields.io/badge/tests-85%20passed-green)]()
[![Coverage](https://img.shields.io/badge/coverage-6%20modules-blue)]()
[![Python](https://img.shields.io/badge/python-3.12+-blue)]()
[![Java](https://img.shields.io/badge/java-21+-orange)]()

## 项目简介

**售后退款决策 Agent** 是一个面向在线教育场景的智能客服辅助决策系统。它通过 LangGraph 工作流编排、LLM 意图识别、RAG 规则检索和确定性业务校验，实现自动化的退款决策建议。

### 解决的问题

在线教育客服处理退款工单时，需要：
1. 理解用户真实诉求和退款原因
2. 查询订单、支付、课程有效期和学习进度
3. 检索当前生效的退款规则
4. 根据确定性业务条件判断退款资格
5. 生成有规则依据的处理建议
6. 对高风险或信息不足的工单转交人工

### 产品定位

**不替代客服，而是辅助客服** —— 完成信息收集、规则检索、资格校验和建议生成。

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Vue 3 前端                              │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST / SSE
─────────────────────▼───────────────────────────────────────┐
│              Spring Boot 3 模块化单体                         │
│  ┌─────────────┐  ┌─────────────┐  ────────────────────┐  │
│  │ 订单/课程   │  │ 退款资格    │  │ 工单/AgentTask      │  │
│  │ 领域服务    │  │ 领域服务    │  │                     │  │
│  └─────────────┘  └─────────────  └─────────────────────┘  │
─────────────────────┬───────────────────────────────────────┘
                      │ Redis Streams
┌─────────────────────▼───────────────────────────────────────┐
│              FastAPI + LangGraph Agent 服务                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ LangGraph   │  │ LLM 集成    │  │ RAG 检索            │  │
│  │ 7 节点工作流│  │ (OpenAI)    │  │ (Elasticsearch)     │  │
│  └─────────────┘  └─────────────┘  ─────────────────────┘  │
─────────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
    ┌────────  ┌──────────┐  ┌─────────┐
    │ Redis  │  │ Elastic  │  │ Langfuse│
    │ 7.x    │  │ Search   │  │ / OTel  │
    └────────  └──────────┘  └─────────┘
```

### 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| Java 服务 | Spring Boot 3, Java 21 | 业务底座、领域服务 |
| Python 服务 | FastAPI, LangGraph | Agent 推理、工作流编排 |
| LLM | OpenAI GPT-4 | 意图识别、建议生成 |
| 检索 | Elasticsearch 8.x | BM25 规则检索 |
| 消息队列 | Redis Streams | 异步任务消费 |
| 可观测性 | Langfuse | Trace 和 Token 记录 |
| 测试 | pytest, JUnit 5 | 单元/集成测试 |

---

## 快速开始

### 1. 环境准备

```bash
# Python 环境
conda create -n refund-agent python=3.12
conda activate refund-agent
cd python-agent
pip install -r requirements.txt

# Java 环境
cd java-service
./gradlew build
```

### 2. 启动依赖服务

```bash
# Docker Compose 一键启动
docker-compose up -d

# 验证服务
curl http://localhost:9200/_cluster/health
curl http://localhost:6379
```

### 3. 导入规则数据

```bash
cd python-agent
python -m app.infrastructure.retrieval.rule_indexer --import data/refund_rules.json
```

### 4. 启动服务

```bash
# Java 服务
cd java-service
./gradlew bootRun

# Python 服务
cd python-agent
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. 运行测试

```bash
# Python 测试
cd python-agent
pytest app/tests/ -v

# 召回率评测
python -m app.tests.retrieval_eval

# 安全测试
pytest app/tests/test_security.py -v
```

---

## 核心功能

### 6 类退款场景

| 场景 | 决策 | 说明 |
|------|------|------|
| 课程无法观看 | 建议退款 | 技术原因导致无法学习 |
| 重复购买 | 建议退款 | 误操作重复下单 |
| 无理由退款 (7 天) | 需审批 | 学习进度 < 10% |
| 超期退款 | 拒绝 | 超过 30 天 |
| 学习进度超限 | 拒绝 | 已学 > 30% |
| 信息不足 | 补充信息 | 缺少订单号等 |

### LangGraph 7 节点工作流

```
[Start] → [分类意图] → [验证字段] → [查询业务数据] → [检索规则]
    → [检查资格] → [生成建议] → [风险检查] → [End]
```

### 安全机制

- **Prompt Injection 防护**: 识别并抵抗注入攻击
- **越权访问控制**: Java 层校验订单归属
- **规则冲突检测**: 多条规则冲突时转人工
- **失败策略**: 超时重试、降级处理、预算控制

---

## 评测结果

### 召回率指标

```
Recall@3:       0.940  (目标 >= 0.8) ✅
Precision@3:    0.934
MRR:            0.881
Total Tests:    160
```

### 测试覆盖

- 160 条测试用例
- 6 类退款场景全覆盖
- 13 个安全测试用例
- 85 个单元/集成测试

### 安全测试

- ✅ Prompt Injection 防护（5 个用例）
- ✅ 越权访问控制（3 个用例）
- ✅ 边界情况处理（5 个用例）

---

## 技术亮点

### 1. DDD + Port/Adapter 架构

- Java 领域模型封装确定性业务逻辑
- Python Port 接口抽象，方便替换 Fake 实现
- 清晰的职责边界和依赖方向

### 2. LangGraph 显式状态图

- 7 节点线性工作流，非 ReAct 循环
- 每个节点有明确的输入/输出/退出条件
- 支持人工审批中断和恢复

### 3. RAG 只负责规则证据

- 退款资格由 Java 确定性计算
- RAG 仅检索规则原文和引用
- 避免模型幻觉影响业务决策

### 4. Redis Streams at-least-once

- 消费组 + XPENDING/XAUTOCLAIM 恢复
- 心跳机制 + 幂等处理
- 崩溃后任务可恢复

### 5. 安全优先设计

- Prompt Injection 检测和防御
- 订单归属校验防止越权
- 规则冲突时保守转人工

---

## 面试问题

### 为什么使用 Agent，而不是固定工作流？

> Agent 能处理信息不完整的情况，通过多轮对话补全字段；固定工作流无法灵活应对缺失信息。

### 为什么退款资格不能由模型判断？

> 模型判断不可审计、不可复现；退款资格涉及金额，必须用确定性代码计算，保证一致性和可追溯性。

### 为什么 RAG 只负责规则证据？

> 规则会持续更新，需要动态检索；但资格判断涉及订单状态、金额计算等实时业务事实，这些由 Java API 提供。

### Redis Streams 消息何时 ACK？

> 只有在 Agent 结果持久化、Token/Trace 记录保存、任务状态更新全部成功后，才执行 XACK。

### Python Worker 宕机后如何恢复？

> 启动时通过 XPENDING 检查未确认消息，XAUTOCLAIM 回收空闲超时的消息，保证 at-least-once 语义。

### 如何避免重复退款？

> 任务幂等性：同一 task_id 多次消费只产生一次业务结果；Java 层校验订单退款历史。

### 规则版本冲突怎么处理？

> 同一场景出现多条有效版本且建议不同决策时，标记冲突并转人工审批。

### 如何证明 Agent 的决策正确？

> 160 条测试集验证，每条决策都有规则引用；评测报告可定位失败发生在哪个节点。

---

## 后续优化

- 主动学习：从人工驳回案例生成新测试样本
- Prompt 和模型灰度发布
- 规则变更自动触发回归测试
- 长期记忆写入审批、TTL 和遗忘机制

---

## 项目结构

```
refund-decision-agent/
├── java-service/                 # Java 业务服务
│   └── src/main/java/
│       ── com.example.aftersale/
│           ├── domain/           # 领域模型
│           ├── application/      # 应用服务
│           └── interfaces/       # REST API
├── python-agent/                 # Python Agent 服务
│   ─ app/
│       ├── agent/                # LangGraph 工作流
│       ├── application/          # Port 接口
│       ├── domain/               # 领域模型
│       ├── infrastructure/       # 基础设施实现
│       ├── api/                  # FastAPI 路由
│       ── tests/                # 测试
── data/                         # 测试数据
── docs/                         # 文档
── docker/                       # Docker 配置
```

---

## 开发阶段

- [x] 阶段 0：问题与评测先行
- [x] 阶段 1：Java 确定性业务底座
- [x] 阶段 2：Python Agent 最小链路
- [x] 阶段 3：RAG 与证据
- [x] 阶段 4：Redis Streams 与持久执行
- [x] 阶段 5：评测、成本和安全
- [ ] 阶段 6：展示与简历证据

---

## 许可证

MIT License

---

## 联系方式

项目作者：YangJW6
