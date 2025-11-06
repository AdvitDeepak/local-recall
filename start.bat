@echo off
REM Startup script for Local Recall on Windows

echo Starting Local Recall...
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist venv\Lib\site-packages\fastapi (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Create .env if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo.
)

REM Start all components
echo Starting all components...
echo Backend will run on port 8000
echo Frontend will run on port 8501
echo.
echo Press Ctrl+C to stop all components
echo.

python main.py all
