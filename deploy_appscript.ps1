# deploy_appscript.ps1 — push appscript.gs live to the Apps Script editor
# One-command replacement for the old manual paste workflow.
#
# Usage (from repo root):
#   .\deploy_appscript.ps1
#
# What it does:
#   1. Copy appscript.gs (repo source of truth) into apps_script\Code.js
#   2. clasp push -f  (force = overwrite live with local)
#   3. Print version banner from the file for visual confirmation

$ErrorActionPreference = "Stop"
$repoRoot = $PSScriptRoot
$src = Join-Path $repoRoot "appscript.gs"
$dst = Join-Path $repoRoot "apps_script\Code.js"
$workDir = Join-Path $repoRoot "apps_script"

if (-not (Test-Path $src)) { throw "Source not found: $src" }
if (-not (Test-Path $workDir)) { throw "clasp workspace missing: $workDir (run 'clasp clone <scriptId>' first)" }

Copy-Item -Path $src -Destination $dst -Force
Write-Host "Synced appscript.gs -> apps_script\Code.js" -ForegroundColor Cyan

Push-Location $workDir
try {
    clasp push -f
} finally {
    Pop-Location
}

$verLine = Select-String -Path $src -Pattern "^const APP_VERSION|// v15\." | Select-Object -First 1
if ($verLine) { Write-Host "Deployed: $($verLine.Line.Trim())" -ForegroundColor Green }
Write-Host "Done. Live editor now reflects current appscript.gs." -ForegroundColor Green
