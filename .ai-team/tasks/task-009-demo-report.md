---
title: "静态 Demo 报告与展示入口"
task_id: "task-009-demo-report"
status: "done"
owner: "codex"
mode: "serial"
work_mode: "MVP"
created: "2026-06-29"
dependencies: task-008-test-smoke-readiness
verification_status: passed
last_run_id: task-009-demo-report-executor-20260629095323
last_result: demo_report_generated_smoke_6_passed_python_91_passed_java_6_passed
blocked_reason:
branch:
github_issue:
github_pr:
ci_status:
tags:
  - ai-team/task
---

# Task: 静态 Demo 报告与展示入口

## Status

- Task ID: `task-009-demo-report`
- Owner: `codex`
- Status: `done`
- Mode: `serial`
- Work Mode: `MVP`
- Dependencies:
- Verification Status: `passed`
- Last Run: `task-009-demo-report-executor-20260629095323`
- Last Result: `demo_report_generated_smoke_6_passed_python_91_passed_java_6_passed`
- Blocked Reason:
- Branch:
- GitHub Issue:
- GitHub PR:
- CI Status:

## Goal

提供一个不需要启动服务的静态 Demo 展示入口：运行离线冒烟后生成 `docs/demo-report.html`，让面试展示可以直接看到用例、决策分布、规则引用、风险提示和证据。

## Non-Goals

- 不引入前端构建链路或新依赖。
- 不改变 Agent 业务逻辑、数据库 schema、API 契约或部署方式。
- 不提交真实 API Key 或本地 `.env`。

## File Boundaries

### Allowed To Modify

- scripts/smoke_demo.py
- docs/demo-report.html
- README.md
- PROJECT_STATUS.md
- .ai-team/tasks/task-009-demo-report.md
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
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe scripts\smoke_demo.py --html
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe -m pytest
mvn test
```

## Handoff Notes

- Changed files: `scripts/smoke_demo.py`, `docs/demo-report.html`, `README.md`, `PROJECT_STATUS.md`.
- Verification result: HTML report generated; 6 demo smoke cases passed; Python pytest 91 passed; Java Maven test 6 passed.
- Run evidence: `task-009-demo-report-executor-20260629095323`.
- Known follow-ups: optional API-backed demo page after local startup flow is stable.
- Memory updates needed: none.

