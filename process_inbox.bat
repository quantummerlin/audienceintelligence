@echo off
cd /d %~dp0
echo.
echo  AI.quantummerlin — Inbox Content Pipeline
echo  ==========================================
echo  Drop .json files OR entire folders into:
echo  %~dp0inbox\
echo.
echo  Then click this file to process everything.
echo.
python process_inbox.py %1
echo.
pause
