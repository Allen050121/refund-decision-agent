# 系统架构文档

## 整体架构

```mermaid
graph TB
    subgraph 前端层
        A[Vue 3 Web 界面]
    end

    subgraph Java 服务层
        B[Spring Boot 3]
        B1[订单领域服务]
        B2[课程领域服务]
        B3[退款资格服务]
        B4[工单管理服务]
    end

    subgraph 消息队列
        C[Redis Streams]
        C1[after-sale:agent:tasks]
        C2[after-sale:agent:events:*]
    end

    subgraph Python Agent 层
        D[FastAPI]
        D1[LangGraph 工作流]
        D2[LLM 集成]
        D3[RAG 检索]
    end

    subgraph 基础设施
        E[Elasticsearch]
        F[Redis]
        G[Langfuse]
    end

    A -->|REST/SSE| B
    B -->|Outbox| C
    C -->|消费| D
    D -->|BM25| E
    D -->|心跳/ACK| F
    D -->|Trace| G
    D -->|HTTP| B1
    D -->|HTTP| B2
    D -->|HTTP| B3

    B1 --> MySQL[(MySQL)]
    B2 --> MySQL
    B3 --> MySQL
    B4 --> MySQL
```

## LangGraph 工作流架构

```mermaid
graph LR
    A[Start] --> B[分类意图]
    B --> C[验证字段]
    C --> D[查询业务数据]
    D --> E[检索规则]
    E --> F[检查资格]
    F --> G[生成建议]
    G --> H[风险检查]
    H --> I[End]

    B -.->|LLM/规则| B
    C -.->|缺失字段| J[信息补全]
    F -.->|需审批| K[人工审批]
    H -.->|高风险| K
```

## 数据流架构

```mermaid
sequenceDiagram
    participant 客服 as 客服前端
    participant Java as Java 服务
    participant Redis as Redis Streams
    participant Python as Python Agent
    participant LLM as OpenAI
    participant ES as Elasticsearch
    participant 审批 as 人工审批

    客服->>Java: 提交退款工单
    Java->>Java: 创建工单记录
    Java->>Redis: 写入任务 Stream
    Java-->>客服: 返回任务 ID

    Redis->>Python: 消费任务
    Python->>LLM: 意图识别
    LLM-->>Python: 返回意图
    Python->>Java: 查询订单
    Java-->>Python: 返回订单
    Python->>Java: 查询学习进度
    Java-->>Python: 返回进度
    Python->>ES: 检索规则
    ES-->>Python: 返回规则
    Python->>Java: 资格校验
    Java-->>Python: 返回结果
    Python->>LLM: 生成建议
    LLM-->>Python: 返回建议
    Python->>Redis: 发布事件
    Python->>Redis: ACK 任务

    alt 需要审批
        Python->>审批: 发送审批请求
        审批->>审批: 人工决策
        审批-->>Python: 审批结果
    end

    Python->>Java: 更新任务状态
    Java-->>客服: SSE 推送结果
```

## 安全架构

```mermaid
graph TB
    subgraph 输入层
        A[用户工单]
    end

    subgraph 安全检查
        B[Prompt Injection 检测]
        C[越权访问控制]
        D[规则冲突检测]
    end

    subgraph 处理层
        E[LangGraph 工作流]
        F[Java 领域服务]
    end

    subgraph 输出层
        G[决策结果]
        H[人工审批]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G -->|高风险| H
    G -->|普通| A
```

## 部署架构

```mermaid
graph TB
    subgraph Docker Compose
        A[Nginx]
        B[Java Service]
        C[Python Agent]
        D[Redis]
        E[Elasticsearch]
        F[MySQL]
    end

    A --> B
    A --> C
    B --> D
    B --> F
    C --> D
    C --> E
    C --> B
```

## 技术选型理由

| 组件 | 选型 | 理由 |
|------|------|------|
| Java 框架 | Spring Boot 3 | 强一致业务、事务、权限 |
| Python 框架 | FastAPI + LangGraph | 模型 SDK、RAG、评测生态 |
| 消息队列 | Redis Streams | 轻量、at-least-once、消费组 |
| 检索引擎 | Elasticsearch | BM25、元数据过滤、混合检索 |
| 可观测性 | Langfuse | Trace、Token 记录、成本分析 |
| 数据库 | MySQL 8 | 业务数据持久化 |

## 扩展性设计

- **LLM 可替换**: 通过 Port 接口抽象，可切换不同模型
- **检索可升级**: BM25 基线，可平滑升级到 Hybrid Search
- **任务可恢复**: Redis Streams 消费组 + XPENDING 恢复
- **规则可更新**: ES 索引支持规则版本管理
