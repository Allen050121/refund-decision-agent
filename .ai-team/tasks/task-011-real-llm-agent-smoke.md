---
title: "真实大模型 Agent 链路与兜底验证"
task_id: "task-011-real-llm-agent-smoke"
status: "done"
owner: "codex"
mode: "serial"
work_mode: "MVP"
created: "2026-06-29"
dependencies: task-010-service-smoke
verification_status: passed
last_run_id: task-011-real-llm-agent-smoke-executor-20260629103233
last_result: real_llm_4_passed_service_7_passed_python_91_passed_java_6_passed
blocked_reason:
branch:
github_issue:
github_pr:
ci_status:
tags:
  - ai-team/task
---

# Task: 真实大模型 Agent 链路与兜底验证

## Status

- Task ID: `task-011-real-llm-agent-smoke`
- Owner: `codex`
- Status: `done`
- Mode: `serial`
- Work Mode: `MVP`
- Dependencies:
- Verification Status: `passed`
- Last Run: `task-011-real-llm-agent-smoke-executor-20260629103233`
- Last Result: `real_llm_4_passed_service_7_passed_python_91_passed_java_6_passed`
- Blocked Reason:
- Branch:
- GitHub Issue:
- GitHub PR:
- CI Status:

## Goal

提供一个真实大模型参与的 Agent 链路冒烟脚本，验证分类、推荐、确定性规则校正、缺字段兜底和非退款请求兜底，作为前端 Demo 与面试展示前的模型链路证据。

## Non-Goals

- 不把真实 API Key 写入仓库或日志。
- 不把真实模型调用放入默认单元测试，避免日常回归依赖外部网关和产生额外成本。
- 不修改业务规则、数据库 schema、部署配置或前端工程。

## File Boundaries

### Allowed To Modify

- scripts/real_llm_agent_smoke.py
- README.md
- PROJECT_STATUS.md
- .ai-team/tasks/task-011-real-llm-agent-smoke.md
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
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe -m py_compile scripts\real_llm_agent_smoke.py
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe scripts\real_llm_agent_smoke.py --timeout 45
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe scripts\service_smoke.py
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe scripts\smoke_demo.py --html
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe -m pytest
mvn test
```

## Handoff Notes

- Changed files: `scripts/real_llm_agent_smoke.py`, `README.md`, `PROJECT_STATUS.md`.
- Verification result: real LLM Agent smoke 4/4 passed with `gpt-5.4-mini @ https://sui-xiang.com/v1`; service smoke 7/7 passed; offline smoke 6/6 passed; Python pytest 91 passed; Java Maven test 6 passed.
- Run evidence: `task-011-real-llm-agent-smoke-executor-20260629103233`.
- Known follow-ups: build the minimal frontend Demo console using these smoke scripts as validation evidence.
- Memory updates needed: none.

