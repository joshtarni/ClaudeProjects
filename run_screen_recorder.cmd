@echo off
cd /d "%~dp0"

py -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Could not install the required packages.
    pause
    exit /b 1
)

py screen_recorder.py
