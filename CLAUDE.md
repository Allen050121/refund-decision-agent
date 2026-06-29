# Claude Code Instructions

This project uses the AI Team workflow.

Read `.ai-team/CLAUDE.md` first, then check:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Get-AiTeamStatus.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Update-AiTeamCollaboration.ps1 -Action status -Client claude
```

Before editing, claim one task with `.ai-team/scripts/Update-AiTeamCollaboration.ps1 -Action start -Client claude -TaskId <task-id> -Role <role>`.
