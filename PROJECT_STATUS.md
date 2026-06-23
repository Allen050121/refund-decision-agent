# 售后退款决策 Agent - 项目状态跟踪

> 最后更新：2026-06-23

## 当前阶段

**阶段 0：问题与评测先行** → 已完成基础框架，准备进入 **阶段 1：Java 确定性业务底座**

---

## 阶段进度

### ✅ 阶段 0：问题与评测先行（框架搭建完成）

| 交付物 | 状态 | 备注 |
|--------|------|------|
| 6 类退款规则 | ⚠️ 待定义 | 需在开发文档中明确 |
| 30 条最小种子测试集 | ✅ 已创建 | tests/seed-dataset.md |
| 指标定义 | ⚠️ 待完善 | 参考文档第9节 |
| 业务决策表 | ❌ 待创建 | 需定义标准答案 |
| API 契约草案 | ⚠️ 部分完成 | 有骨架，需完善 |
| 数据库 Schema | ✅ 已完成 | java-service/src/main/resources/sql/ |

**退出条件检查：**
- ❌ 不调用模型也能根据标准答案判断测试是否通过（需完成业务决策表）

---

### 🔄 阶段 1：Java 确定性业务底座（下一步）

| 实现内容 | 状态 | 优先级 |
|----------|------|--------|
| 用户、订单、课程领域模型 | ❌ 待实现 | P0 |
| 学习进度实体 | ❌ 待实现 | P0 |
| 工单与 AgentTask 领域模型 | ❌ 待实现 | P0 |
| 退款资格领域服务 | ❌ 待实现 | P0 |
| 订单归属和权限校验 | ❌ 待实现 | P0 |
| Flyway 数据脚本 | ✅ 已创建 | - |
| 单元测试 | ❌ 待编写 | P1 |
| Testcontainers 集成测试 | ❌ 待编写 | P1 |

**退出条件：**
- 退款资格规则测试全部通过
- 重复请求不会产生重复业务结果

---

## 环境配置状态

| 组件 | 地址 | 状态 |
|------|------|------|
| Java Service | localhost:8080 | ✅ 可启动 |
| Python Agent | localhost:8000 | ✅ 依赖已安装 |
| MySQL | 192.168.85.66:3306 | ⚠️ 需创建数据库 |
| Redis | 192.168.85.66:6379 | ✅ 虚拟机运行 |
| Elasticsearch | 192.168.85.66:9200 | ✅ 虚拟机运行 |

---

## 技术栈确认

| 技术 | 版本 | 状态 |
|------|------|------|
| Java | 21 | ✅ 已安装 |
| Spring Boot | 3.2.0 | ✅ pom.xml 配置 |
| Maven | 3.9.9 | ✅ 已安装 |
| Python | 3.12 | ✅ Miniconda 环境 |
| FastAPI | 最新 | ✅ 已安装 |
| LangGraph | 最新 | ✅ 已安装 |

---

## 下一步任务卡

### 任务 #1：创建数据库和执行 SQL

**描述：** 在虚拟机 MySQL 中创建 refund_agent 数据库和表结构

**步骤：**
1. 连接虚拟机 MySQL (192.168.85.66:3306)
2. 执行 `01-create-database.sql`
3. 执行 `02-create-tables.sql`
4. 执行 `03-seed-data.sql`（可选，测试数据）

**验证：** 能查询到 users、orders、courses 等表

---

### 任务 #2：实现 Java 领域模型（阶段 1 核心）

**描述：** 按文档 4.3 代码结构实现领域模型

**目录结构：**
```
com.example.aftersale
├── domain
│   ├── support/        # 工单领域
│   ├── refund/         # 退款领域
│   ├── agenttask/      # Agent任务领域
│   └── shared/         # 共享值对象
```

**值对象（按文档要求）：**
- `OrderId`
- `UserId`
- `Money`（使用整数分，禁止浮点数）
- `RuleVersion`
- `TokenUsage`

**优先级：** P0 - 必须完成才能进入阶段 2

---

### 任务 #3：定义业务决策表（阶段 0 收尾）

**描述：** 为 30 条测试样本定义标准答案，满足阶段 0 退出条件

**输出格式：**
```json
{
  "testId": "Test-001",
  "expectedDecision": "REFUND_RECOMMENDED",
  "expectedAmount": 19900,
  "expectedRuleId": "REFUND-2026-003",
  "expectedEvidence": ["ORDER_PAID", "COURSE_UNAVAILABLE"]
}
```

---

## Git 提交记录

| 时间 | Commit | 描述 |
|------|--------|------|
| 2026-06-22 | 9b5a1e0 | Initial project setup |
| 2026-06-22 | ecb1c2b | Add environment setup guide |
| 2026-06-23 | 8b7c73a | Update configuration for VM |

---

## 备注

- **开发文档位置：** `01-售后决策Agent-MVP产品与开发文档.md`
- **GitHub 仓库：** https://github.com/Allen050121/refund-decision-agent
- **AI Team Workflow：** `.ai-team/` 已初始化