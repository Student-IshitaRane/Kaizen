@echo off
echo Setting up Audit Analytics Platform Backend...
echo.

echo Step 1: Installing dependencies...
pip install -r minimal_requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Checking project structure...
python test_setup.py
if %errorlevel% neq 0 (
    echo Project structure check failed
    pause
    exit /b 1
)

echo.
echo Step 3: Creating uploads directory...
if not exist uploads mkdir uploads

echo.
echo Step 4: Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your database configuration
echo 2. Initialize database: python scripts/init_database.py
echo 3. Run backend: python run.py
echo 4. Access API docs: http://localhost:8000/docs
echo.
pause