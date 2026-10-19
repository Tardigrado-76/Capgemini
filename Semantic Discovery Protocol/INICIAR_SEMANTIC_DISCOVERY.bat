@echo off
title QUANTIGRADE - Semantic Discovery Protocol (SDP) - Progressive Disclosure
color 0B
echo =====================================================================
echo       QUANTIGRADE - SEMANTIC DISCOVERY PROTOCOL (PORT 8510)
echo         Universal Canonical Connector Reference Model
echo            Ahorro del 85-94%% de Tokens de Contexto
echo =====================================================================
echo.
echo Iniciando Cockpit Ejecutivo Streamlit (Quantigrade - Detalle Iwan)...
echo Por favor, espere unos instantes mientras se carga el registro de capacidades...
echo.

cd /d "%~dp0"
python -m streamlit run app_streamlit.py --server.port 8510 --server.headless false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo iniciar Streamlit. Verifique su entorno de Python.
    pause
)
