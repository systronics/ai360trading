@echo off
title AI360Trading — Smart Sync
color 0A
echo ============================================
echo    AI360Trading Smart Sync System
echo    Checking PC vs GitHub for latest files
echo ============================================
echo.
cd C:\Users\Admin\ai360trading

REM Step 1: Fetch latest info from GitHub without merging
echo [1/5] Fetching GitHub status...
git fetch origin
echo.

REM Step 2: Show which files differ between PC and GitHub
echo [2/5] Files that differ between PC and GitHub:
git diff --stat HEAD origin/master
echo.

REM Step 3: Check if GitHub has newer commits
FOR /F "tokens=*" %%i IN ('git rev-list HEAD..origin/master --count') DO SET AHEAD=%%i
FOR /F "tokens=*" %%i IN ('git rev-list origin/master..HEAD --count') DO SET BEHIND=%%i

echo GitHub has %AHEAD% new commit(s) you don't have on PC
echo PC has %BEHIND% new commit(s) not on GitHub yet
echo.

REM Step 4: Smart merge — take latest from both sides
echo [3/5] Syncing latest files...
git pull --rebase origin master
echo.

REM Step 5: Push PC changes to GitHub
echo [4/5] Pushing PC changes to GitHub...
git add .
set TIMESTAMP=%date% %time%
git commit -m "SmartSync: %TIMESTAMP%" 2>nul
git push origin master
echo.

REM Step 6: Update LOCAL sync log (SESSION.md is PC-only, never pushed)
echo [5/5] Updating local sync log...
echo Last SmartSync: %TIMESTAMP% >> SESSION.md

echo.
echo ============================================
echo    SYNC COMPLETE — PC and GitHub identical
echo    Open Claude Code and type: claude
echo ============================================
pause
