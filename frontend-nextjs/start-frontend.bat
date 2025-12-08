@echo off
echo Starting Local Recall Frontend...
echo.

cd /d "%~dp0"

if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

echo Starting Next.js development server on port 3000...
call npm run dev
