---
title: "阶段 4: Redis Streams 异步任务 - 消费组与心跳机制"
task_id: "TASK-004"
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
last_result: "72_tests_passed,redis_streams_verified"
blocked_reason:
branch: "master"
github_issue:
github_pr:
ci_status:
tags:
  - ai-team/task
  - phase-4
  - redis
  - streams
  - async
---

# Task: 阶段 4 Redis Streams 异步任务

## Status

- Task ID: `TASK-004`
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

实现 Redis Streams 异步任务消费机制，支持消费组、心跳、自动恢复和事件发布。

## Task Layer

- Task Type: `implementation`
- Delivery Stage: `stack`
- This card is allowed to produce: Redis Streams 消费者、事件发布器、消费组管理
- This card must not skip: XPENDING/XAUTOCLAIM 恢复、心跳机制、幂等处理
- Next expected card: `TASK-005` (可观测性与 Langfuse 集成)

## Product Decisions

- Audience: 系统内部任务调度
- Primary pain: 同步处理超时风险，需要异步任务队列
- MVP use case: Java 创建任务写入 Redis Stream，Python 消费并处理
- Product surface: Redis Streams + 消费组 + 心跳
- Confirmed stack choices: redis-py, XPENDING, XAUTOCLAIM
- Scale/capacity assumption: MVP 单消费组，低并发

## Questions For Human Lead

1. **是否需要多消费者并行？**
   - 默认：MVP 单消费者，后续扩展消费组

2. **任务失败重试策略？**
   - 默认：有限重试后进入死信队列

## Non-Goals

- 不实现复杂多消费者负载均衡
- 不实现任务优先级队列
- 不实现实时任务监控面板
- 不实现自动扩缩容

## Product Surface And UX Source

- Source screens/pages: 系统内部
- User actions: Java 写入任务，Python 消费处理
- Components involved: Redis Streams, 消费组，心跳
- Loading/empty/error states: 消费失败进入死信队列

## API And Business Mapping

| 功能 | 输入 | 输出 |
|------|------|------|
| 任务消费 | Redis Stream | 处理结果 |
| 事件发布 | taskId, event | Stream 写入 |
| 心跳更新 | consumer_id | 时间戳更新 |

## File Boundaries

### Allowed To Modify

```
python-agent/
├── app/
│   ├── infrastructure/
│   │   └── redis_stream/
│   │       ├── consumer.py        # 消费者实现（已有框架）
│   │       ├── event_publisher.py # 事件发布器（已有框架）
│   │       └── tests/             # 测试（新增）
│   └── tests/
│       ── test_redis_stream.py   # 集成测试（新增）
└── docker/
    └── docker-compose.yml         # Redis 配置（如有）
```

### Must Not Modify

- `java-service/` 目录下的任何文件
- `app/domain/` 下的领域模型

## Context To Read

- `01-售后决策 Agent-MVP 产品与开发文档.md` - 文档 4.3 异步任务
- `.ai-team/tasks/TASK-002-python-agent-workflow.md` - 阶段 2 任务卡
- `python-agent/app/infrastructure/redis_stream/consumer.py` - 现有消费者框架
- `python-agent/app/infrastructure/redis_stream/event_publisher.py` - 现有事件发布器

## Implementation Notes

### 消费组设计

```python
STREAM_NAME = "after-sale:agent:tasks"
CONSUMER_GROUP = "after-sale-agent-workers"
CONSUMER_NAME = "worker-1"

# 消费循环
while True:
    messages = await xreadgroup(
        groupname=CONSUMER_GROUP,
        consumername=CONSUMER_NAME,
        streams={STREAM_NAME: ">"},
        count=10,
        block=5000,
    )
    
    for stream, msgs in messages:
        for msg_id, fields in msgs:
            await process_task(fields)
            await xack(STREAM_NAME, CONSUMER_GROUP, msg_id)
```

### 心跳机制

```python
# 每 30 秒更新心跳
async def heartbeat():
    while True:
        await set(f"consumer:{CONSUMER_NAME}:heartbeat", time.time(), ex=60)
        await asyncio.sleep(30)
```

### 恢复机制

```python
# 启动时恢复未确认消息
pending = await xpending(STREAM_NAME, CONSUMER_GROUP)
for msg in pending:
    if time.time() - msg.last_delivery > 60:
        await xautoclaim(
            STREAM_NAME,
            CONSUMER_GROUP,
            CONSUMER_NAME,
            min_idle_time=60000,
        )
```

## Acceptance Criteria

- [ ] Redis 连通性测试通过
- [ ] 消费组创建成功
- [ ] 任务消费与 ACK 正常
- [ ] 心跳机制工作正常
- [ ] XPENDING 恢复逻辑正确
- [ ] 事件发布到独立 Stream
- [ ] 单元测试覆盖核心逻辑
- [ ] 集成测试通过

## Verification

```bash
# 启动 Redis（如果未运行）
docker run -d -p 6379:6379 redis:7

# 运行测试
cd python-agent
pytest app/tests/test_redis_stream.py -v

# 手动测试
python -m app.infrastructure.redis_stream.consumer
```

## Handoff Notes

- Changed files:
- Verification result:
- Run evidence:
- Known follow-ups: TASK-005 可观测性与 Langfuse 集成
- Memory updates needed:
