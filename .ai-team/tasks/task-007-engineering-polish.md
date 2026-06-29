---
title: "工程质量与 AI Team 状态收口"
task_id: "task-007-engineering-polish"
status: "done"
owner: "codex"
mode: "serial"
work_mode: "MVP"
created: "2026-06-29"
dependencies: TASK-006
verification_status: passed
last_run_id: task-007-engineering-polish-executor-20260629004224
last_result: java_build_success_python_88_passed_no_warnings
blocked_reason:
branch:
github_issue:
github_pr:
ci_status:
tags:
  - ai-team/task
  - polish
  - resume
---

# Task: 工程质量与 AI Team 状态收口

## Status

- Task ID: `task-007-engineering-polish`
- Owner: `codex`
- Status: `done`
- Mode: `serial`
- Work Mode: `MVP`
- Dependencies: `TASK-006`
- Verification Status: `passed`
- Last Run: `task-007-engineering-polish-executor-20260629004224`
- Last Result: `java_build_success_python_88_passed_no_warnings`

## Goal

让项目从“功能完成”进入“简历展示/面试追问更稳”的状态：修复工程警告、清理测试弃用提示、补齐 AI Team 记忆和仓库索引，并同步任务状态，确保 Codex 和 Claude 后续都能读到一致上下文。

## Non-Goals

- 不新增业务功能。
- 不改变退款决策规则、Agent 节点语义、RAG 召回策略或接口契约。
- 不提交真实 API Key 或本地 `.env`。
- 不启动/重启由 Human Lead 管理的 Java/Python 服务进程。

## File Boundaries

### Allowed To Modify

- `java-service/pom.xml`
- `python-agent/app/**`
- `.ai-team/memory/project-brief.md`
- `.ai-team/index/repo-map.md`
- `.ai-team/state/*.json`
- `.ai-team/tasks/TASK-001-java-domain-model.md`
- `.ai-team/tasks/task-007-engineering-polish.md`
- `PROJECT_STATUS.md`

### Must Not Modify

- Business data migrations unless explicitly needed.
- Secret-bearing files such as `python-agent/.env`.
- Completed task cards other than status/evidence corrections.

## Context To Read

- `PROJECT_STATUS.md`
- `README.md`
- `01-售后决策Agent-MVP产品与开发文档.md`
- `.ai-team/memory/project-brief.md`
- `.ai-team/index/repo-map.md`
- `.ai-team/state/tasks.json`
- `.ai-team/state/runs.json`

## Implementation Notes

- Prefer small quality fixes that reduce warnings without changing behavior.
- Keep AI Team memory compact and factual.
- Record verification evidence after Java and Python tests pass.

## Acceptance Criteria

- [x] Maven duplicate dependency warning is removed.
- [x] Python pytest deprecation warnings from project code are removed.
- [x] Python tests pass in the configured conda environment.
- [x] Java `mvn test` build succeeds.
- [x] `.ai-team/memory/project-brief.md` has real project facts instead of TODOs.
- [x] `.ai-team/index/repo-map.md` has a compact accurate repository map.
- [x] `TASK-001` is marked completed/passed to match implementation state.
- [x] Run evidence is recorded in `.ai-team/state/runs.json`.

## Verification

```powershell
cd java-service
mvn test

cd ../python-agent
D:/yangjw/software/Miniconda/envs/refund-agent/python.exe -m pytest
```

## Handoff Notes

- Changed files: Maven dependency cleanup, Python timezone/Redis close cleanup, AI Team memory/repo-map/status updates, PROJECT_STATUS update.
- Verification result: `java-service: mvn test => BUILD SUCCESS`; `python-agent: conda python -m pytest => 88 passed, no warnings`.
- Run evidence: `task-007-engineering-polish-executor-20260629004224`
- Known follow-ups: add focused Java unit tests for `RefundEligibilityService` to strengthen interview evidence.
- Memory updates needed: completed in `project-brief.md` and `repo-map.md`.
