@echo off
title QUANTIGRADE - Compliance-as-Code Live Mesh (PORT 8507)
color 0B
echo =====================================================================
echo    QUANTIGRADE - COMPLIANCE-AS-CODE LIVE MESH (PORT 8507)
echo     Auditoria Regulatoria Continua para Proyectos Capgemini
echo   Cumplimiento DORA, NIS2, ENS RD 311/2022 y EU AI Act (Art. 12)
echo =====================================================================
echo.
echo Iniciando servidor ejecutivo Streamlit...
echo Por favor, espere unos instantes mientras se carga el tejido vivo...
echo.

cd /d "%~dp0"
python -m streamlit run app_streamlit.py --server.port 8507 --server.headless false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo iniciar Streamlit. Verifique su entorno de Python.
    pause
)
