@echo off
REM BIOCORE AI — Script de ejecución para Windows

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║         BIOCORE AI — Plataforma de Inteligencia Biomédica    ║
echo ║                   Iniciando aplicación...                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en el PATH
    echo.
    echo Para instalar Python:
    echo 1. Ve a https://www.python.org/downloads/
    echo 2. Descarga Python 3.9 o superior
    echo 3. Durante la instalación, marca "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Mostrar versión de Python
echo ✓ Python instalado:
python --version
echo.

REM Verificar que streamlit está instalado
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit no instalado. Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error instalando dependencias
        pause
        exit /b 1
    )
)

echo ✓ Dependencias verificadas
echo.

REM Mostrar opciones de ejecución
echo Selecciona cómo ejecutar la aplicación:
echo.
echo 1) App principal (RECOMENDADO) — http://localhost:8501
echo 2) Academia Inteligente — Misiones, pacientes, gemelo digital
echo 3) ECG Monitor — Análisis de ECG
echo 4) Tutor IA — Chatbot interactivo
echo 5) Salir
echo.

set /p choice="Ingresa tu opción (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Iniciando aplicación principal...
    echo.
    streamlit run app/main.py
) else if "%choice%"=="2" (
    echo.
    echo 🚀 Iniciando Academia Inteligente...
    echo.
    streamlit run app/pages/12_Academia_Inteligente.py
) else if "%choice%"=="3" (
    echo.
    echo 🚀 Iniciando ECG Monitor...
    echo.
    streamlit run app/pages/1_ECG_Monitor.py
) else if "%choice%"=="4" (
    echo.
    echo 🚀 Iniciando Tutor IA...
    echo.
    streamlit run app/main.py -- --logger.level=off
) else if "%choice%"=="5" (
    echo.
    echo ¡Hasta luego!
    exit /b 0
) else (
    echo.
    echo ❌ Opción inválida
    pause
    exit /b 1
)
