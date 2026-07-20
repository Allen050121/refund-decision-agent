# 售后退款决策 Agent - 项目状态跟踪

> 最后更新：2026-07-20

## 当前阶段

项目已进入 **MVP 部署演示可用** 阶段。

核心功能、评测材料、公开文档、Demo 控制台和服务器部署均已完成；当前重点是保持演示环境稳定、避免真实密钥入库，并在需要时补充域名和 HTTPS。

---

## 阶段进度

| 阶段 | 状态 | 说明 |
|------|------|------|
| 阶段 0：问题与评测先行 | ✅ 完成 | 已有固定测试集与评测口径 |
| 阶段 1：Java 确定性业务底座 | ✅ 完成 | 已实现领域模型、退款资格校验、权限边界 |
| 阶段 2：Python Agent 最小链路 | ✅ 完成 | 已实现 FastAPI、LangGraph 工作流、Java API 客户端 |
| 阶段 3：RAG 与证据 | ✅ 完成 | 已实现 Elasticsearch BM25、规则数据、召回率评测 |
| 阶段 4：Redis Streams 与持久执行 | ✅ 完成 | 已实现消费组、心跳、XPENDING/XAUTOCLAIM 恢复 |
| 阶段 5：评测、成本和安全 | ✅ 完成 | 已扩展到 160 条测试查询，安全测试文档已生成 |
| 阶段 6：项目文档与 Demo 展示 | ✅ 完成 | README、架构文档、评测报告、Demo 控制台、Docker Compose 已生成 |
| 当前收尾：真实 LLM 连通 | ✅ 已切到可用 OpenAI-compatible 网关 | `https://sui-xiang.com/v1` + `gpt-5.4-mini` 已通过项目 LLM client 最小推理验证 |
| 当前收尾：工程质量与 AI Team 状态 | ✅ 完成 | Maven 重复依赖告警已清理，Python pytest 弃用警告已清零，项目记忆与 repo map 已补齐 |
| 当前收尾：测试数据与冒烟验证 | ✅ 完成 | 已新增 6 条离线金标冒烟用例、Java 领域规则单测，并补齐缺失字段/非退款请求的最终决策断言 |
| 当前收尾：静态 Demo 展示入口 | ✅ 完成 | `scripts/smoke_demo.py --html` 可生成 `docs/demo-report.html`，直接展示冒烟结果、决策分布、规则引用和风险提示 |
| 当前收尾：启动后服务级冒烟 | ✅ 完成 | `scripts/service_smoke.py` 可在 Java/Python 启动后验证健康检查、SQL 种子查询和退款资格接口 |
| 当前收尾：真实大模型 Agent 链路 | ✅ 完成 | `scripts/real_llm_agent_smoke.py` 已用 `gpt-5.4-mini @ https://sui-xiang.com/v1` 验证分类、推荐和兜底链路 |
| 当前收尾：最小前端 Demo 控制台 | ✅ 完成 | Python 服务重启后访问 `http://localhost:8000/demo`，可选择工单并调用真实 `/tasks` Agent 链路 |
| 当前收尾：服务器部署 | ✅ 完成 | `http://175.178.6.214/demo`、`/health`、`/health/ready` 已可访问，Java jar + Python conda + Nginx 反代运行，Python 服务端口为 8001 |

---

## 当前事实

- AI Team 任务状态：`.ai-team/state/tasks.json` 中 `TASK-000` 到 `TASK-006` 均为 `completed`，新增 `task-007-engineering-polish` 和 `task-008-test-smoke-readiness` 跟踪工程质量与测试冒烟收口。
- 测试数据：`python-agent/data/test_queries.json` 当前为 160 条。
- 规则数据：`python-agent/data/refund_rules.json` 当前为 10 条。
- 展示材料：`README.md`、`docs/architecture.md`、`docs/evaluation_report.md`、`docs/demo-report.html` 已存在。
- 本地 `.env` 已切到可用 OpenAI-compatible 中转站：`LLM_BASE_URL=https://sui-xiang.com/v1`、`LLM_MODEL=gpt-5.4-mini`，真实 API Key 只保存在 `python-agent/.env`，不得提交。

---

## 最新修复点

### LLM 中转站连接配置

已将 Python LLM 客户端改为 OpenAI-compatible 配置：

- `LLM_BASE_URL` 控制模型网关地址。
- `LLM_MODEL` 控制模型名。
- `OPENAI_API_KEY` 继续作为兼容 API Key 字段。
- `LLM_PROXY_URL` 为可选代理；为空时不再强制走 `127.0.0.1:7897`。

这避免了本地代理端口未启动时导致 Freemodel/DeepSeek 请求全部连不通。

### Java 退款资格接口

已补齐产品文档要求的：

```http
POST /api/refund/check-eligibility
```

当前 8080 上的旧进程需要重启后才会加载此接口。临时使用 8081 启动当前代码验证过以下 SQL 种子数据场景：

- `O20260622001 / U1001 / NO_REASON`：可退款，最大退款 19900 分。
- `O20260622003 / U1002 / COURSE_UNAVAILABLE`：可退款，最大退款 17900 分。
- `O20260622002 / U1001 / NO_REASON`：学习进度超限，不可退款。

### 工程质量与 AI Team 状态收口

已完成本轮工程质量清理：

- 删除 Java `pom.xml` 中重复的 `spring-boot-starter-data-redis` 依赖，`mvn test` 不再输出重复依赖 warning。
- 将 Python 项目内 `datetime.utcnow()` 替换为 timezone-aware UTC 时间，清理 Pydantic/Python 3.13 相关弃用警告。
- 将 Redis async 连接关闭从 deprecated `close()` 改为 `aclose()`。
- 补齐 `.ai-team/memory/project-brief.md` 和 `.ai-team/index/repo-map.md`，让 Codex/Claude 都能稳定读取项目定位、目录和验证命令。
- 修正 `TASK-001` 状态为 completed/passed，使任务状态与 Java 代码事实一致。

### 测试数据与离线冒烟验证

- 新增 `python-agent/data/demo_cases.json`，提供 6 条 Demo 金标用例：推荐退款、拒绝退款、人工审批、缺失信息和非退款咨询。
- 新增 `scripts/smoke_demo.py`，使用 Fake LLM、Fake Retriever 和用例内业务快照离线执行 Agent 核心节点，不依赖 Java、Redis、Elasticsearch 或真实模型网关。
- 收紧 Agent 风险闸口：缺失必要字段或非退款意图时，最终决策必须收敛为 `NEED_MORE_INFORMATION`，避免冒烟测试“表面 PASS 但实际给退款建议”。
- 新增 Java 领域规则单元测试，覆盖课程不可用、无理由退款、进度超限、越权订单、未支付订单和异常退款用户审批。

### 静态 Demo 展示入口

- `scripts/smoke_demo.py` 支持 `--json` 和 `--html`，可在同一次离线冒烟运行后输出机器可读报告或静态 HTML。
- `docs/demo-report.html` 已生成，可直接打开，展示 6 条用例的意图、原因、决策、规则引用、风险提示和证据。
- 该展示入口不引入前端工程依赖，不需要启动服务，适合用于离线结果展示和回归对比。

### 启动后服务级冒烟

- 新增 `scripts/service_smoke.py`，用于项目服务已经启动后的真实接口验证。
- 默认检查 Java `http://localhost:8080` 的 `/health`、订单查询、学习进度、课程状态和 `POST /api/refund/check-eligibility`。
- 默认也检查 Python `http://localhost:8000` 的 `/health` 和 `/health/ready`；如只验证 Java，可加 `--skip-python`。
- 当前环境未由 Codex 启动服务时该脚本会失败并提示启动/重启服务后重试，这是预期行为。

### 真实大模型 Agent 链路验证

- 新增 `scripts/real_llm_agent_smoke.py`，专门调用本地 `.env` 中配置的 OpenAI-compatible 大模型，不进入默认单元测试，避免日常测试产生外部依赖和额外成本。
- 已验证模型：`gpt-5.4-mini @ https://sui-xiang.com/v1`。
- 覆盖 4 条关键用例：课程不可用退款推荐、模型泛化时规则校正、缺少订单号补充信息、非退款咨询兜底。
- 真实模型链路验证仍注入本地业务快照和 Fake RAG，目的是把测试焦点放在 LLM/Agent 编排边界，而不是 Java/ES 可用性。

### 最小前端 Demo 控制台

- 新增 Python 服务内置页面 `/demo`，不引入 Node/Vite 等前端构建依赖。
- 页面提供 6 条 demo 工单、健康状态、运行决策、轮询任务结果、规则引用、证据和风险提示展示。
- 页面调用同源真实 `/tasks` 接口；当 Python 服务以真实大模型配置启动时，前端演示会进入真实 Agent 链路。
- 当前已通过 ASGI 测试验证 `/demo` 页面可返回；如果服务已经在旧代码上运行，需要重启 Python 服务后访问。

---

## 验证状态

| 验证项 | 当前结果 | 备注 |
|--------|----------|------|
| Java `mvn test` | ✅ Build Success | 6 个 JUnit 领域规则测试通过 |
| Python 语法编译 | ✅ 通过 | `python -m compileall app` 通过 |
| Python pytest | ✅ 通过 | 使用 `D:\yangjw\software\Miniconda\envs\refund-agent\python.exe`，`91 passed`，本轮弃用警告已清零 |
| 离线金标冒烟 | ✅ 通过 | `python scripts/smoke_demo.py`，6 条 demo cases 全部 PASS，且不再连接外部 Java API |
| 静态 Demo 报告 | ✅ 通过 | `python scripts/smoke_demo.py --html` 已生成 `docs/demo-report.html` |
| 启动后服务级冒烟 | ✅ 脚本已就绪 | `python scripts/service_smoke.py`，需先启动 Java/Python 服务；当前未启动时会明确失败 |
| 真实大模型 Agent 冒烟 | ✅ 通过 | `python scripts/real_llm_agent_smoke.py --timeout 45`，4 条真实模型链路与兜底用例全部 PASS |
| 前端 Demo 控制台 | ✅ 通过 | ASGI 测试 `/demo` 返回页面，页面包含真实 `/tasks` 调用入口 |
| Freemodel `/models` | ✅ 通过 | `cc.freemodel.dev/v1/models` 返回 200，包含 `claude-sonnet-4-6` |
| Freemodel 推理调用 | ⚠️ 后端不可用 | `/chat/completions` 和 `/messages` 均返回 503 Service Unavailable |
| Sui-xiang `/models` | ✅ 通过 | `https://sui-xiang.com/v1/models` 返回 200，包含多个 GPT 模型 |
| Sui-xiang 推理调用 | ✅ 通过 | `gpt-5.4-mini` 和 `gpt-5.4` 可用；项目当前使用 `gpt-5.4-mini` |
| Java SQL 种子查询接口 | ✅ 通过 | 订单、学习进度、课程状态接口已用 SQL 种子数据验证 |
| Java 退款资格接口 | ✅ 通过 | 本地代码验证通过，服务器 8080 已随 `refund-java` 服务生效 |
| 服务器服务级冒烟 | ✅ 通过 | 服务器运行 `scripts/service_smoke.py`，7 项检查全部通过 |
| 服务器真实 `/tasks` 链路 | ✅ 通过 | 已返回 `COMPLETED / REFUND_RECOMMENDED`，规则引用包含 `REFUND-2026-001` |

---

## 下一步建议

1. 绑定正式域名，并用 HTTPS 证书替换当前 HTTP 访问。
2. Elasticsearch 镜像拉取稳定后，将服务器 `ELASTICSEARCH_URL=fake` 切回真实 ES，并重新导入 `python-agent/data/refund_rules.json`。
3. Freemodel 推理接口后续可再重试；当前 key 鉴权没问题，但后端返回 503。
4. 当前数据库里的中文课程名/故障原因返回存在乱码，SQL 文件和表结构是 `utf8mb4`，更像是既有数据导入时客户端编码不对；需要时用 UTF-8 客户端重导种子数据。

---

## 注意事项

- 不要把 `python-agent/.env` 或真实 API Key 提交到 Git。
- `README.md` 和 `.ai-team` 状态已按 MVP 完成理解；后续新增工作建议新建 `TASK-007`，不要继续把连通性修复塞进展示任务里。
