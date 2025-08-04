@echo off
echo ========================================
echo JSON Formatter - Production Mode
echo ========================================
echo.

REM Check Python versions in order of preference
set PYTHON_CMD=
set PIP_CMD=

REM Try Python 3 first
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    set PIP_CMD=pip3
    goto :python_found
)

REM Try python command
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    set PIP_CMD=pip
    goto :python_found
)

REM Try py launcher with Python 3
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3
    set PIP_CMD=py -3 -m pip
    goto :python_found
)



echo ERROR: Python is not installed or not in PATH
pause
exit /b 1

:python_found
echo Found Python:
%PYTHON_CMD% --version
echo.

REM Set production environment variables
set FLASK_ENV=production
set FLASK_DEBUG=0
set FLASK_HOST=0.0.0.0
set FLASK_PORT=5000

echo Environment: Production
echo Debug Mode: Disabled
echo Host: %FLASK_HOST%
echo Port: %FLASK_PORT%
echo.

REM Install dependencies
if not exist requirements.txt (
    echo ERROR: requirements.txt not found
    pause
    exit /b 1
)

echo Installing dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo First attempt failed, trying alternative method...
    %PIP_CMD% install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo Try running as administrator or update Python
        pause
        exit /b 1
    )
)

echo.
echo Starting JSON Formatter in Production Mode...
echo.
echo The application will be available at: http://localhost:%FLASK_PORT%
echo Press Ctrl+C to stop the application
echo.

%PYTHON_CMD% app.py

pause