@echo off
echo ========================================
echo JSON Formatter Application
echo ========================================
echo.

REM Check Python versions in order of preference
set PYTHON_CMD=
set PYTHON_VERSION=

REM Try py launcher with Python 3 first (most reliable on Windows)
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3
    set PIP_CMD=py -3 -m pip
    goto :python_found
)

REM Try python command and check if it's Python 3
python --version 2>&1 | findstr /C:"Python 3" >nul
if not errorlevel 1 (
    set PYTHON_CMD=python
    set PIP_CMD=python -m pip
    goto :python_found
)

REM Try python3 command (less common on Windows)
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    set PIP_CMD=python3 -m pip
    goto :python_found
)



echo ERROR: Python is not installed or not in PATH
echo.
echo Please install Python from https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation
echo.
pause
exit /b 1

:python_found
echo Found Python:
%PYTHON_CMD% --version

REM Verify it's Python 3.x
%PYTHON_CMD% --version 2>&1 | findstr /C:"Python 3" >nul
if errorlevel 1 (
    echo ERROR: Python 3.x is required, but found an older version
    echo Please install Python 3.x from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
echo.

REM Check if requirements.txt exists
if not exist requirements.txt (
    echo ERROR: requirements.txt not found
    echo Please make sure you are in the correct directory
    pause
    exit /b 1
)

REM Try to install dependencies with different methods
echo Installing dependencies...
echo Trying: %PIP_CMD% install -r requirements.txt
%PIP_CMD% install -r requirements.txt
if not errorlevel 1 (
    echo Dependencies installed successfully!
    goto :start_app
)

echo.
echo First attempt failed, trying alternative method...
echo Trying: %PYTHON_CMD% -m pip install -r requirements.txt
%PYTHON_CMD% -m pip install -r requirements.txt
if not errorlevel 1 (
    echo Dependencies installed successfully!
    goto :start_app
)

echo.
echo Second attempt failed, trying to upgrade pip first...
echo Trying: %PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install --upgrade pip
if not errorlevel 1 (
    echo Pip upgraded, now installing dependencies...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if not errorlevel 1 (
        echo Dependencies installed successfully!
        goto :start_app
    )
)

echo.
echo ERROR: Failed to install dependencies
echo.
echo Possible solutions:
echo 1. Update Python to a newer version
echo 2. Run as administrator
echo 3. Try manual installation: %PYTHON_CMD% -m pip install -r requirements.txt
echo 4. Check your internet connection
echo.
pause
exit /b 1

:start_app
echo.
echo Starting JSON Formatter Application...
echo.
echo The application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.

%PYTHON_CMD% app.py

pause