@echo off
TITLE Quantigrade - Detalle Iwan ^| Maestro Swarm CLI
COLOR 0B
chcp 65001 >nul
set PYTHONUTF8=1

echo ===============================================================================
echo     QUANTIGRADE - DETALLE IWAN (MAESTRO SWARM TERMINAL CLI)
echo ===============================================================================
echo.

cd /d "%~dp0"
python -m orchestrator

pause
