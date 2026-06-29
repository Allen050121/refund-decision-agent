---
title: "测试数据与冒烟验证收口"
task_id: "task-008-test-smoke-readiness"
status: "done"
owner: "codex"
mode: "serial"
work_mode: "MVP"
created: "2026-06-29"
dependencies: task-007-engineering-polish
verification_status: passed
last_run_id: task-008-test-smoke-readiness-executor-20260629094041
last_result: smoke_6_passed_python_91_passed_java_6_passed
blocked_reason:
branch:
github_issue:
github_pr:
ci_status:
tags:
  - ai-team/task
---

# Task: 测试数据与冒烟验证收口

## Status

- Task ID: `task-008-test-smoke-readiness`
- Owner: `codex`
- Status: `done`
- Mode: `serial`
- Work Mode: `MVP`
- Dependencies:
- Verification Status: `passed`
- Last Run: `task-008-test-smoke-readiness-executor-20260629094041`
- Last Result: `smoke_6_passed_python_91_passed_java_6_passed`
- Blocked Reason:
- Branch:
- GitHub Issue:
- GitHub PR:
- CI Status:

## Goal

让测试数据和冒烟验证能支撑简历项目展示：提供可重复的离线金标用例、Java 领域规则单测、Python Agent 回归断言，并在 README/项目状态中写清验证命令。

## Non-Goals

- 不新增完整前端。
- 不改变数据库 schema、认证、支付或部署配置。
- 不依赖真实 API Key、Java 服务、Redis、Elasticsearch 或模型网关才能完成基础冒烟。

## File Boundaries

### Allowed To Modify

- java-service/src/test/**
- python-agent/app/agent/nodes/**
- python-agent/app/tests/**
- python-agent/data/demo_cases.json
- scripts/**
- README.md
- PROJECT_STATUS.md
- .ai-team/tasks/task-008-test-smoke-readiness.md
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
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe scripts\smoke_demo.py
D:\yangjw\software\Miniconda\envs\refund-agent\python.exe -m pytest
mvn test
```

## Handoff Notes

- Changed files: Java refund domain tests, Python demo cases, offline smoke script, Agent risk gate assertions, README, PROJECT_STATUS.
- Verification result: `scripts/smoke_demo.py` 6/6 PASS; Python pytest 91 passed; Java Maven test 6 passed / Build Success.
- Run evidence: `task-008-test-smoke-readiness-executor-20260629094041`.
- Known follow-ups: optional minimal demo UI or API-level smoke can be considered after startup flow is stable.
- Memory updates needed: none; README and PROJECT_STATUS already record current testing posture.

