@echo off
REM NIS2 Field Audit Tool - Windows Launcher
REM Usage: nis2-audit.bat

cd /d "%~dp0"
python -m app.textual_app %*
