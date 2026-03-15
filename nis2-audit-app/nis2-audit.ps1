# NIS2 Field Audit Tool - PowerShell Launcher
# Usage: .\nis2-audit.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

& python -m app.textual_app @args
