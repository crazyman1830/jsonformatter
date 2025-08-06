@echo off
echo ========================================
echo JSON Formatter - Development Mode
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

REM Set development environment variables
set FLASK_ENV=development
set FLASK_DEBUG=1
set FLASK_HOST=127.0.0.1
set FLASK_PORT=5000

echo Environment: Development
echo Debug Mode: Enabled
echo Host: %FLASK_HOST%
echo Port: %FLASK_PORT%
echo.

REM Install dependencies if needed
if not exist requirements.txt (
    echo ERROR: requirements.txt not found
    pause
    exit /b 1
)

echo Installing/updating dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some dependencies may not have been installed properly
    echo Trying alternative installation method...
    %PIP_CMD% install -r requirements.txt >nul 2>&1
)

echo.
echo Starting JSON Formatter in Development Mode...
echo.
echo The application will be available at: http://%FLASK_HOST%:%FLASK_PORT%
echo Auto-reload is enabled - changes will be reflected automatically
echo Press Ctrl+C to stop the application
echo.

%PYTHON_CMD% app.py

pause
