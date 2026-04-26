@echo off
cd /d %~dp0
echo.
echo  AI.quantummerlin — Inbox Content Pipeline
echo  ==========================================
echo  Drop .json datasets into inbox/ then click run.
echo.
python process_inbox.py %1
echo.
pause
