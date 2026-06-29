---
title: Claude Code Usage
tags:
  - ai-team
  - claude
status: active
---

# Claude Code Usage

Use Claude Code as an AI Team client that shares the same `.ai-team` state with Codex.

Claude may execute, review, and hand off work, but it must not treat chat history as the source of truth. The source of truth is the project-local `.ai-team` directory.

## Required Startup

Before planning or editing, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Get-AiTeamStatus.ps1
```

Then inspect active collaboration:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Update-AiTeamCollaboration.ps1 -Action status -Client claude
```

If working on a specific task, load compact context:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Get-AiTeamContext.ps1 -TaskId <task-id> -Mode compact
```

Before editing, start a collaboration session:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Update-AiTeamCollaboration.ps1 -Action start -Client claude -TaskId <task-id> -Role executor
```

## Non-Negotiable Rules

- Do not edit implementation files before checking `.ai-team/state/collaboration.json`.
- Do not edit the same task or files as an active Codex session unless acting as reviewer or after explicit Human Lead approval.
- Work from a task card with file boundaries, acceptance criteria, and verification.
- Run verification or record a clear waiver.
- Record compact evidence in `.ai-team/state/runs.json`.
- On stop, hand off or complete the collaboration session.

## Completion

When task work is finished:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Update-AiTeamRun.ps1 -TaskId <task-id> -Role executor -Status passed -Verification "<command>: passed"
powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Update-AiTeamCollaboration.ps1 -Action complete -Client claude -TaskId <task-id>
```

When stopping mid-task:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Update-AiTeamCollaboration.ps1 -Action handoff -Client claude -TaskId <task-id> -Role executor -Summary "Changed X; verified Y" -NextAction "Do Z first"
```

## Routing

- Product idea or broad feature request: act as Dispatcher.
- Implementation task: act as Executor only after starting a collaboration session.
- Review/audit/check: act as Reviewer and do not modify implementation files unless the review requires a small, clearly scoped fix.
- Deployment/release/merge: act as Integration Gate and ask the Human Lead before external or production actions.
- Retrospective/lessons: act as Memory Curator.

Prefer compact context. Use full context only for review, debugging stale memory, or resolving contradictions.
