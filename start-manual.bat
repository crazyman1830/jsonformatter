@echo off
echo ========================================
echo JSON Formatter - Manual Installation
echo ========================================
echo.
echo This script will help you run the application
echo even if automatic dependency installation fails.
echo.

REM Check Python versions in order of preference
set PYTHON_CMD=
echo Checking for Python installations...

REM Try py launcher with Python 3 first (most reliable on Windows)
py -3 --version >nul 2>&1
if not errorlevel 1 (
    echo Found: py -3 (Python Launcher)
    set PYTHON_CMD=py -3
    goto :python_found
)

REM Try python command and check if it's Python 3
python --version 2>&1 | findstr /C:"Python 3" >nul
if not errorlevel 1 (
    echo Found: python (Python 3.x)
    set PYTHON_CMD=python
    goto :python_found
)

REM Try python3 command (less common on Windows)
python3 --version >nul 2>&1
if not errorlevel 1 (
    echo Found: python3
    set PYTHON_CMD=python3
    goto :python_found
)

echo ERROR: Python 3.x is not installed or not in PATH
echo Please install Python 3.x from https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation
pause
exit /b 1

:python_found

echo.
echo Using: %PYTHON_CMD%
%PYTHON_CMD% --version

REM Verify it's Python 3.x
%PYTHON_CMD% --version 2>&1 | findstr /C:"Python 3" >nul
if errorlevel 1 (
    echo ERROR: Python 3.x is required, but found an older version
    echo Please install Python 3.x from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

echo ========================================
echo Manual Dependency Installation
echo ========================================
echo.
echo If automatic installation failed, try these commands manually:
echo.
echo 1. %PYTHON_CMD% -m pip install --upgrade pip
echo 2. %PYTHON_CMD% -m pip install -r requirements.txt
echo.
echo Press any key to try automatic installation, or Ctrl+C to exit and run manually
pause >nul

echo Trying to install dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Automatic installation failed.
    echo Please run these commands manually in Command Prompt:
    echo.
    echo %PYTHON_CMD% -m pip install --upgrade pip
    echo %PYTHON_CMD% -m pip install -r requirements.txt
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.

echo ========================================
echo Starting Application
echo ========================================
echo.
echo The application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.

%PYTHON_CMD% app.py

pause