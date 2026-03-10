@echo off
REM AI Triage System - Windows Startup Script
REM Usage: run.bat [backend|frontend|all]

echo ========================================
echo   AI Triage System - Startup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.9 or higher.
    exit /b 1
)
echo [SUCCESS] Python is installed

REM Check dependencies
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Dependencies not installed. Installing...
    pip install -r requirements.txt
    echo [SUCCESS] Dependencies installed
) else (
    echo [SUCCESS] Dependencies are installed
)

echo.

REM Parse command
if "%~1"=="" goto run_all
if "%~1"=="backend" goto run_backend
if "%~1"=="frontend" goto run_frontend
if "%~1"=="all" goto run_all

echo Usage: %0 [backend^|frontend^|all]
echo.
echo Commands:
echo   backend   - Start only the FastAPI backend
echo   frontend  - Start only the Streamlit dashboard
echo   all       - Start both backend and frontend (default)
exit /b 1

:run_backend
echo [INFO] Starting FastAPI Backend Server...
echo [INFO] API will be available at: http://localhost:8000
echo [INFO] API Documentation: http://localhost:8000/docs
echo ----------------------------------------
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
goto end

:run_frontend
echo [INFO] Starting Streamlit Dashboard...
echo [INFO] Dashboard will be available at: http://localhost:8501
echo ----------------------------------------
streamlit run frontend/dashboard.py
goto end

:run_all
echo [INFO] Starting AI Triage System (Backend + Frontend)...
echo.
echo [INFO] Backend will be available at: http://localhost:8000
echo [INFO] Frontend will be available at: http://localhost:8501
echo.
echo ========================================

REM Start backend in new window
start "AI Triage Backend" uvicorn backend.main:app --host 0.0.0.0 --port 8000

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
start "AI Triage Frontend" streamlit run frontend/dashboard.py

echo.
echo [SUCCESS] Both services are starting!
echo [INFO] Check the opened windows for the services
echo.
pause

:end
