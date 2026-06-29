param(
    [ValidateSet("dispatcher", "executor", "reviewer", "memory", "integration")]
    [string]$Role = "dispatcher",

    [string]$TaskId,

    [switch]$Full
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$configPath = Join-Path $ProjectRoot ".ai-team\config.json"
$collaborationScript = Join-Path $ProjectRoot ".ai-team\scripts\Update-AiTeamCollaboration.ps1"

if (-not (Test-Path -LiteralPath $configPath)) {
    throw "Missing config: $configPath"
}

$config = Get-Content -LiteralPath $configPath -Encoding UTF8 -Raw | ConvertFrom-Json

function Write-Section {
    param(
        [string]$Title,
        [string]$Path,
        [int]$Tail = 0
    )

    $fullPath = Join-Path $ProjectRoot $Path
    Write-Host ""
    Write-Host "===== ${Title}: $Path ====="

    if (-not (Test-Path -LiteralPath $fullPath)) {
        Write-Host "Missing: $fullPath"
        return
    }

    if ($Tail -gt 0 -and -not $Full) {
        Get-Content -LiteralPath $fullPath -Encoding UTF8 -Tail $Tail
    }
    else {
        Get-Content -LiteralPath $fullPath -Encoding UTF8
    }
}

Write-Host "AI TEAM AUTO-CONTEXT"
Write-Host "Role: $Role"
Write-Host "Project: $ProjectRoot"
if ($TaskId) {
    Write-Host "Task: $TaskId"
}

Write-Host ""
Write-Host "Operating instruction:"
Write-Host "- Follow the loaded role prompt."
Write-Host "- Use the memory files as durable project context."
Write-Host "- Stay inside the task card boundaries."
Write-Host "- Do not skip the relevant gate checklist."
Write-Host "- Check collaboration state before editing when Codex and Claude may share this project."

if (Test-Path -LiteralPath $collaborationScript) {
    Write-Host ""
    Write-Host "===== Collaboration State ====="
    & $collaborationScript -Action status -Client other
    Write-Host ""
    Write-Host "Before editing, claim the task with:"
    Write-Host "powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Update-AiTeamCollaboration.ps1 -Action start -Client <codex|claude> -TaskId <task-id> -Role $Role"
}

$rolePrompt = $config.rolePrompts.$Role
if ($rolePrompt) {
    Write-Section "Role Prompt" $rolePrompt
}

foreach ($memoryFile in $config.memoryFiles) {
    Write-Section "Memory" $memoryFile 120
}

if ($TaskId) {
    Write-Section "Task Card" ".ai-team/tasks/$TaskId.md"
}

$bundle = $config.hookBundles.$Role
if ($bundle) {
    foreach ($path in $bundle) {
        if ($path -ne $rolePrompt) {
            Write-Section "Role Bundle" $path
        }
    }
}

Write-Host ""
Write-Host "===== Next Action ====="
switch ($Role) {
    "dispatcher" { Write-Host "Output task decomposition, dependencies, file boundaries, acceptance criteria, and verification commands. Do not implement." }
    "executor" { Write-Host "Implement only the assigned task. End with changed files, verification result, risks, and handoff notes." }
    "reviewer" { Write-Host "Inspect changed files first, then diff, then verification evidence. Return pass, request changes, or blocked." }
    "memory" { Write-Host "Update pitfalls or patterns only when the lesson is durable and reusable." }
    "integration" { Write-Host "Merge only reviewed tasks, run full checks, and document deployment readiness." }
}
