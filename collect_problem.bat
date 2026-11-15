@echo off
cd /d "%~dp0"
python collect_problem.py %*
echo.
echo Report saved in problem_report.txt - open it, copy all, paste into the AI.
pause
