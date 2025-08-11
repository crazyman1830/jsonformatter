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

REM --- Virtual Environment Setup ---
set VENV_DIR=venv
set VENV_PYTHON=%VENV_DIR%\Scripts\python.exe
set VENV_NEEDS_CREATION=0

REM Check if the virtual environment exists and is valid
if exist %VENV_PYTHON% (
    echo Found existing virtual environment. Verifying...
    %VENV_PYTHON% --version 2>&1 | findstr /C:"Python 3" >nul
    if errorlevel 1 (
        echo WARNING: The existing virtual environment in '%VENV_DIR%' seems corrupted or uses a non-Python 3 version.
        echo Deleting the old environment to recreate it.
        rmdir /s /q %VENV_DIR% >nul 2>&1
        set VENV_NEEDS_CREATION=1
    ) else (
        echo Virtual environment is valid.
    )
) else (
    set VENV_NEEDS_CREATION=1
)

REM Create the virtual environment if it's marked for creation
if %VENV_NEEDS_CREATION% equ 1 (
    echo Creating virtual environment in '%VENV_DIR%'...
    %PYTHON_CMD% -m venv %VENV_DIR%
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate.bat

REM Check if requirements.txt exists
if not exist requirements.txt (
    echo ERROR: requirements.txt not found
    echo Please make sure you are in the correct directory
    pause
    exit /b 1
)

echo Installing dependencies...
REM Inside a venv, 'python' and 'pip' are sufficient.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies from requirements.txt
    echo Please check your internet connection and the contents of requirements.txt
    pause
    exit /b 1
)

:start_app
echo.
echo Starting JSON Formatter Application...
echo.
echo The application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.

python app.py

pause
