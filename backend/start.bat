@echo off
REM Backend startup script for development (Windows)

echo PDF Research Assistant Backend - Development Setup
echo ==================================================

REM Check Python version
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Initialize application
echo Initializing application...
python init_app.py

REM Run application
echo Starting application on http://0.0.0.0:8000
echo API Documentation: http://localhost:8000/docs
echo ==================================================

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
