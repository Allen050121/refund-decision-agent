---
title: "最小前端 Demo 控制台"
task_id: "task-012-demo-console"
status: "done"
owner: "codex"
mode: "serial"
work_mode: "MVP"
created: "2026-06-29"
dependencies: task-011-real-llm-agent-smoke
verification_status: passed
last_run_id: task-012-demo-console-executor-20260629104130
last_result: demo_route_test_passed_real_llm_4_passed_service_7_passed_python_92_passed_java_6_passed
blocked_reason:
branch:
github_issue:
github_pr:
ci_status:
tags:
  - ai-team/task
---

# Task: 最小前端 Demo 控制台

## Status

- Task ID: `task-012-demo-console`
- Owner: `codex`
- Status: `done`
- Mode: `serial`
- Work Mode: `MVP`
- Dependencies:
- Verification Status: `passed`
- Last Run: `task-012-demo-console-executor-20260629104130`
- Last Result: `demo_route_test_passed_real_llm_4_passed_service_7_passed_python_92_passed_java_6_passed`
- Blocked Reason:
- Branch:
- GitHub Issue:
- GitHub PR:
- CI Status:

## Goal

提供一个最小前端 Demo 控制台，挂载在 Python 服务 `/demo`，可选择 demo 工单、查看服务健康状态、创建真实 `/tasks` Agent 任务并轮询展示决策、规则引用、证据和风险提示。

## Non-Goals

- 不引入 Node/Vite 等前端构建依赖。
- 不绕过 `/tasks` 直接伪造 Agent 结果。
- 不修改数据库 schema、部署配置或真实 API Key。

## File Boundaries

### Allowed To Modify

- python-agent/app/api/demo.py
- python-agent/app/main.py
- python-agent/app/tests/test_tasks_api.py
- README.md
- PROJECT_STATUS.md
- .ai-team/tasks/task-012-demo-console.md
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
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe -m pytest app/tests/test_tasks_api.py
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe -m pytest
mvn test
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe scripts\real_llm_agent_smoke.py --timeout 45
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe scripts\service_smoke.py
```

## Handoff Notes

- Changed files: `python-agent/app/api/demo.py`, `python-agent/app/main.py`, `python-agent/app/tests/test_tasks_api.py`, `README.md`, `PROJECT_STATUS.md`.
- Verification result: `/demo` ASGI route test passed; Python pytest 92 passed; Java Maven test 6 passed; real LLM smoke 4/4 passed; service smoke 7/7 passed.
- Run evidence: `task-012-demo-console-executor-20260629104130`.
- Known follow-ups: restart Python service so the running process loads `/demo`; then open `http://localhost:8000/demo`.
- Memory updates needed: none.

