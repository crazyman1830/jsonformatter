@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo JSON Formatter - One-Click Start
echo ========================================
echo.

REM --- Check for Node.js ---
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js ^(npm^) is not found in PATH.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM --- Check for Python ---
set PYTHON_CMD=
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3
) else (
    python --version 2>&1 | findstr /C:"Python 3" >nul
    if not errorlevel 1 (
        set PYTHON_CMD=python
    )
)

if "%PYTHON_CMD%"=="" (
    echo ERROR: Python 3 is not found.
    echo Please install Python 3 from https://www.python.org/
    pause
    exit /b 1
)

echo Found Python: %PYTHON_CMD%
echo Found Node.js
echo.

REM --- Frontend Setup ---
echo [1/3] Setting up Frontend...
cd frontend

if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
    if !errorlevel! neq 0 (
        echo ERROR: Failed to install frontend dependencies.
        pause
        exit /b 1
    )
)

echo Building frontend...
call npm run build
if !errorlevel! neq 0 (
    echo ERROR: Failed to build frontend.
    pause
    exit /b 1
)

cd ..
echo Frontend build complete.
echo.

REM --- Backend Setup ---
echo [2/3] Setting up Backend...

set VENV_DIR=venv
if not exist %VENV_DIR% (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv %VENV_DIR%
)

echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate.bat

echo Installing backend dependencies...
pip install -r requirements.txt >nul
if !errorlevel! neq 0 (
    echo ERROR: Failed to install backend dependencies.
    pause
    exit /b 1
)
echo Backend setup complete.
echo.

REM --- Start Application ---
echo [3/3] Starting Application...
echo.
echo The application will be available at: http://localhost:5000
echo Press Ctrl+C to stop.
echo.

python app.py

pause
