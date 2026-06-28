# 简历项目描述草稿

## 项目一：售后退款决策 Agent（推荐）

**项目名称**: 售后退款决策 Agent | RAG + Tool Calling + Human-in-the-loop

**项目描述**:
面向在线教育场景的智能客服辅助决策系统，通过 LangGraph 工作流编排、LLM 意图识别、RAG 规则检索和确定性业务校验，实现自动化退款决策建议。

**技术栈**: Java 21, Spring Boot 3, Python 3.12, FastAPI, LangGraph, OpenAI, Elasticsearch, Redis Streams

**核心职责**:
- 设计并实现 DDD + Port/Adapter 架构，Java 承载确定性业务逻辑，Python 承载 Agent 推理
- 实现 LangGraph 7 节点显式状态图，支持人工审批中断和恢复
- 实现 Elasticsearch BM25 检索，召回率达 94%，支持元数据过滤和规则冲突检测
- 实现 Redis Streams at-least-once 消费，支持 XPENDING 恢复和心跳机制
- 实现 Prompt Injection 防护和越权访问控制，通过 13 个安全测试用例

**项目成果**:
- 6 类退款场景全覆盖，160 条测试集验证
- 退款资格由 Java 确定性计算，避免模型幻觉
- 崩溃后任务可恢复，保证业务连续性

---

## 项目二：智能客服 RAG 系统

**项目名称**: 基于 RAG 的智能客服规则检索系统

**项目描述**:
为客服决策提供规则证据支持，通过 Elasticsearch 实现退款规则的动态检索和版本管理，确保决策依据的可追溯性。

**技术栈**: Elasticsearch 8.x, Python, BM25, Pydantic v2

**核心职责**:
- 设计 ES 索引结构，支持规则编号、场景、生效时间等元数据过滤
- 实现 BM25 基线检索，Recall@3 达 94%
- 实现规则版本管理，支持生效/失效/冲突检测
- 构建 160 条标准测试集，覆盖口语化表达、同义词、边界情况

**项目成果**:
- 规则检索准确率 93.4%
- 支持规则冲突时自动转人工审批
- 过期规则不会进入有效检索结果

---

## 项目三：异步任务处理系统

**项目名称**: 基于 Redis Streams 的异步任务处理系统

**项目描述**:
实现高可靠的异步任务消费机制，支持消费组、心跳、自动恢复和事件发布，保证 at-least-once 语义。

**技术栈**: Redis 7.x, Python, asyncio, 消费组

**核心职责**:
- 实现 Redis Streams 消费组，支持多消费者并行
- 实现 XPENDING + XAUTOCLAIM 恢复机制，崩溃后任务可恢复
- 实现心跳机制和幂等处理，防止重复消费
- 实现事件发布器，支持进度通知和断线续传

**项目成果**:
- 任务恢复成功率 100%
- 支持断线续传和进度追踪
- 通过 8 个集成测试验证

---

## 项目四：AI Agent 安全评测

**项目名称**: AI Agent 安全评测与防护系统

**项目描述**:
针对 LLM 应用的 Prompt Injection、越权访问等安全威胁，建立完整的评测体系和防护机制。

**技术栈**: Python, pytest, LangGraph

**核心职责**:
- 设计 Prompt Injection 测试用例（5 类攻击）
- 实现越权访问控制测试（订单归属校验）
- 实现边界情况测试（超长输入、特殊字符）
- 构建 13 个安全测试用例，通过率 100%

**项目成果**:
- 100% 抵抗 Prompt Injection 攻击
- 100% 阻止越权访问
- 100% 处理边界情况

---

## 面试亮点总结

### 技术深度
- DDD + Port/Adapter 架构设计
- LangGraph 显式状态图 vs ReAct 循环
- RAG 只负责证据，决策由确定性代码计算
- Redis Streams at-least-once 语义实现

### 业务理解
- 退款资格不能由模型判断（涉及金额、可审计性）
- 规则冲突时保守转人工
- 崩溃后任务必须可恢复

### 工程能力
- 85 个单元/集成测试，100% 通过
- 160 条测试集，Recall@3 达 94%
- Docker Compose 一键启动
- 完整的可观测性（Langfuse Trace）

### 安全意识
- Prompt Injection 防护
- 越权访问控制
- 规则版本管理
- 失败策略（重试、降级、预算控制）
