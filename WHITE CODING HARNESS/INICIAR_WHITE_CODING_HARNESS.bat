@echo off
title QUANTIGRADE - WHITE CODING HARNESS - Proof Machine de Especificacion
color 0B
echo =====================================================================
echo    QUANTIGRADE - WHITE CODING HARNESS - PROOF MACHINE (PORT 8506)
echo      Paradigma White Coding (Iwan Rochus van der Kleijn)
echo    Cumplimiento EU AI Act Art. 12, SLSA L3+ y Directiva NIS2
echo =====================================================================
echo.
echo Iniciando servidor ejecutivo Streamlit...
echo Por favor, espere unos instantes mientras se cargan los motores de contrato...
echo.

cd /d "%~dp0"
python -m streamlit run app_streamlit.py --server.port 8506 --server.headless false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo iniciar Streamlit. Verifique su entorno de Python.
    pause
)
