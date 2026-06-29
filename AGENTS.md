# AI Team Project Instructions

This project uses the AI Team workflow.

Codex should read `.ai-team/CODEX.md`, `.ai-team/README.md`, `.ai-team/memory/`, `.ai-team/tasks/`, `.ai-team/state/tasks.json`, `.ai-team/state/runs.json`, and `.ai-team/state/collaboration.json` before planning or editing.

Before editing in a shared Codex/Claude project:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Get-AiTeamStatus.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Update-AiTeamCollaboration.ps1 -Action status -Client codex
```

Then claim exactly one task:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Update-AiTeamCollaboration.ps1 -Action start -Client codex -TaskId <task-id> -Role <role>
```

Claude Code should read `CLAUDE.md` and `.ai-team/CLAUDE.md`.
