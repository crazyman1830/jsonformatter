@echo off
REM Code quality check script for Windows

echo Running code quality checks...

echo.
echo [1/4] Running Black formatter check...
python -m black --check src/
if %errorlevel% neq 0 (
    echo Black formatting check failed!
    exit /b 1
)

echo.
echo [2/4] Running Flake8 linter...
python -m flake8 src/
if %errorlevel% neq 0 (
    echo Flake8 linting failed!
    exit /b 1
)

echo.
echo [3/4] Running MyPy type checker...
python -m mypy src/ --config-file pyproject.toml
if %errorlevel% neq 0 (
    echo MyPy type checking failed!
    exit /b 1
)

echo.
echo [4/4] Running Bandit security checker...
python -m bandit -r src/ --configfile pyproject.toml
if %errorlevel% neq 0 (
    echo Bandit security check failed!
    exit /b 1
)

echo.
echo All code quality checks passed! ✓
