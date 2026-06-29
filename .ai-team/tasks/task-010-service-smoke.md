---
title: "启动后服务级冒烟脚本"
task_id: "task-010-service-smoke"
status: "done"
owner: "codex"
mode: "serial"
work_mode: "MVP"
created: "2026-06-29"
dependencies: task-009-demo-report
verification_status: passed
last_run_id: task-010-service-smoke-executor-20260629101934
last_result: service_smoke_ready_pytest_91_passed_java_6_passed
blocked_reason:
branch:
github_issue:
github_pr:
ci_status:
tags:
  - ai-team/task
---

# Task: 启动后服务级冒烟脚本

## Status

- Task ID: `task-010-service-smoke`
- Owner: `codex`
- Status: `done`
- Mode: `serial`
- Work Mode: `MVP`
- Dependencies:
- Verification Status: `passed`
- Last Run: `task-010-service-smoke-executor-20260629101934`
- Last Result: `service_smoke_ready_pytest_91_passed_java_6_passed`
- Blocked Reason:
- Branch:
- GitHub Issue:
- GitHub PR:
- CI Status:

## Goal

提供一个项目启动后的真实服务冒烟脚本：用户启动 Java/Python 服务后，一条命令检查健康接口、SQL 种子数据查询接口和 Java 退款资格接口，补齐离线 demo 到真实运行之间的验证链路。

## Non-Goals

- 不启动或停止本地服务，项目启动仍由用户控制。
- 不修改业务逻辑、数据库 schema、API 契约或部署配置。
- 不提交真实 API Key 或本地 `.env`。

## File Boundaries

### Allowed To Modify

- scripts/service_smoke.py
- README.md
- PROJECT_STATUS.md
- .ai-team/tasks/task-010-service-smoke.md
- .ai-team/state/*.json

### Must Not Modify

- Files outside the allowed boundary unless this card is updated first.
- Shared schemas, migrations, auth, payment, or build configuration unless explicitly listed above.

## Context To Read

- `.ai-team/memory/project-brief.md`
- `.ai-team/memory/production-mode.md`
- `.ai-team/memory/technology-policy.md`
- `.ai-team/memory/pitfalls.md`
- `.ai-team/memory/patterns.md`
- `.ai-team/commands.json`
- `.ai-team/policies/command-policy.md`
- Related source files listed above.

## Implementation Notes

- Keep the change small enough for one reviewer to inspect quickly.
- Prefer existing project patterns over new abstractions.
- If boundaries are wrong, stop and update this card before editing.
- Create or use a task branch when code changes are required.
- Keep GitHub issue/PR fields updated when GitHub is used for the project.
- Record execution or review evidence in `.ai-team/state/runs.json`.

## Acceptance Criteria

- [x] Goal is implemented.
- [x] File boundary was respected or this card was updated.
- [x] Diff has no unrelated edits.
- [x] Pitfalls were checked.
- [x] Verification command was run or explicitly waived with a reason.
- [x] Security-sensitive changes passed `.ai-team/checklists/security-gate.md`.
- [x] PR/CI status is recorded when GitHub is used.
- [x] Run evidence was recorded in `.ai-team/state/runs.json`.

## Verification

```powershell
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe -m py_compile scripts\service_smoke.py
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe scripts\service_smoke.py --help
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe scripts\service_smoke.py --skip-python --timeout 0.5
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe -m pytest
mvn test
```

## Handoff Notes

- Changed files: `scripts/service_smoke.py`, `README.md`, `PROJECT_STATUS.md`.
- Verification result: script compiles; help output works; service-not-running path fails clearly; Python pytest 91 passed; Java Maven test 6 passed.
- Run evidence: `task-010-service-smoke-executor-20260629101934`.
- Known follow-ups: run `scripts/service_smoke.py` again after the user starts Java/Python services.
- Memory updates needed: none.

