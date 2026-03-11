@echo off
echo Starting Audit Analytics Platform Backend...
echo.

echo Checking dependencies...
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r minimal_requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Testing setup...
python quick_test.py
if %errorlevel% neq 0 (
    echo Setup test failed
    pause
    exit /b 1
)

echo.
echo Starting backend server...
echo API will be available at: http://localhost:8000
echo Press Ctrl+C to stop
echo.

python run.py