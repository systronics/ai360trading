@echo off
rem backup_pc_docs.bat - copies the PC-only notes + memory to the PRIVATE repo ai360trading-backup and pushes. Run daily by Windows Task Scheduler (only when the PC is on).
set SRC=C:\Users\Admin\ai360trading
set BK=C:\Users\Admin\ai360trading-backup
set MEM=C:\Users\Admin\.claude\projects\C--Users-Admin-ai360trading\memory
if not exist "%BK%\.git" (
  echo Backup repo not cloned yet. Run once:  git clone https://github.com/systronics/ai360trading-backup.git "%BK%"
  exit /b 1
)
if not exist "%BK%\pc" mkdir "%BK%\pc"
if not exist "%BK%\pc\memory" mkdir "%BK%\pc\memory"
for %%F in (SESSION.md .internal-ops.md CHANGELOG.md TRADING_PLAYBOOK.md GROWTH_PLAYBOOK.md PROJECT_HANDOFF.md) do (
  if exist "%SRC%\%%F" copy /Y "%SRC%\%%F" "%BK%\pc\%%F" >nul
)
if exist "%SRC%\tradingview" xcopy /Y /E /I /Q "%SRC%\tradingview" "%BK%\pc\tradingview" >nul
if exist "%MEM%" xcopy /Y /E /I /Q "%MEM%" "%BK%\pc\memory" >nul
cd /d "%BK%"
git add -A
git diff --cached --quiet && (echo nothing changed & exit /b 0)
git commit -q -m "pc notes backup %DATE% %TIME%" || (echo COMMIT FAILED & exit /b 1)
git push -q || (echo PUSH FAILED & exit /b 1)
echo backup pushed
