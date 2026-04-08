@echo off
title Audience Intelligence Report Generator
echo.
echo ========================================
echo  Audience Intelligence Report Generator
echo ========================================
echo.

cd /d "%~dp0"

:: Step 1: Convert .txt to .json if a new .txt exists and is newer than the .json
if exist redditopenclaw.txt (
    if not exist redditopenclaw.json (
        echo [1/2] Converting redditopenclaw.txt to JSON...
        python convert_to_json.py
        echo.
    ) else (
        echo [1/2] redditopenclaw.json already exists. Skipping conversion.
        echo       (Delete redditopenclaw.json first if you have new data.)
        echo.
    )
) else (
    echo [1/2] No redditopenclaw.txt found. Using existing redditopenclaw.json
    echo.
)

:: Step 2: Generate the HTML report
echo [2/2] Generating HTML report...
python generate_openclaw_report.py
echo.

:: Step 3: Open the report in the default browser
echo Opening report in browser...
start "" "outputs\report_openclaw_reddit_2026-03-15.html"

echo.
echo Done!
pause
