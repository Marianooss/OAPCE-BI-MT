@echo off
REM OAPCE Multitrans - Clean Start Script for Windows
REM This script kills any existing processes and starts fresh

echo 🚀 Starting OAPCE Multitrans (Clean Start)...
echo 📊 Dashboard for Grupo OM
echo.
echo 🔧 Steps:
echo    1. Killing existing processes...
echo    2. Starting fresh application...
echo    3. Opening in browser...
echo.

REM Kill any existing processes on port 5001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5001') do (
    taskkill /F /PID %%a 2>nul && echo    ✅ Process %%a terminated
)

REM Kill any Streamlit processes
taskkill /F /IM streamlit.exe 2>nul && echo    ✅ Streamlit processes terminated

REM Kill any Python processes that might be using the port
powershell -Command "Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

echo.
echo 🌐 Starting application on port 5001...
echo 📱 Access at: http://localhost:5001
echo.

REM Start the application
start streamlit run app.py --server.port 5001 --server.address 0.0.0.0 --server.headless true

REM Wait a moment then check if it's running
timeout /t 3 /nobreak >nul
echo.
echo ✅ Application should be running now!
echo 🔗 Open http://localhost:5001 in your browser
echo.
pause
