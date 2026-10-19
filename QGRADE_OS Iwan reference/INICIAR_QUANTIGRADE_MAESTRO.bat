@echo off
TITLE Quantigrade - Detalle Iwan ^| The Maestro Cockpit
COLOR 0B
chcp 65001 >nul
set PYTHONUTF8=1

echo ===============================================================================
echo     QUANTIGRADE - DETALLE IWAN (ECOSISTEMA UNIFICADO 2026-2027)
echo     Capgemini Engineering / White Coding Architecture Practice
echo     Consola Ejecutiva Maestra "The Maestro Cockpit" (:8500)
echo ===============================================================================
echo.
echo [1/3] Verificando entorno Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta disponible en el PATH.
    pause
    exit /b 1
)

echo [2/3] Verificando suite de tests qgrade_core...
python -m pytest tests/test_qgrade_suite.py -q
if %errorlevel% neq 0 (
    echo [WARN] Algunas pruebas fallaron, revise logs.
)

echo [3/3] Iniciando Consola Web Ejecutiva en Puerto Maestro 8500...
echo.
echo URL de acceso local: http://localhost:8500
echo Presiona Ctrl+C en esta ventana para detener el servidor.
echo ===============================================================================
echo.

python -m streamlit run app_quantigrade_maestro.py --server.port 8500 --server.headless false

pause
