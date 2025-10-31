@echo off
REM OAPCE Multitrans - Clean Start Script for the NEW UNIFIED App
echo 🚀 Starting the UNIFIED OAPCE Application...
echo.
echo 🔧 Steps:
echo    1. Killing existing processes on port 8501...
echo    2. Starting fresh application...
echo.

REM Kill any existing processes on port 8501
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501') do (
    taskkill /F /PID %%a 2>nul && echo    ✅ Process %%a on port 8501 terminated
)

echo.
echo 🌐 Starting application on port 8501...
echo 📱 Access at: http://localhost:8501
echo.

REM Start the NEW application
start streamlit run StreamlitBase/Home.py --server.port 8501

echo.
echo ✅ Application should be running now!
echo 🔗 Open http://localhost:8501 in your browser
echo.
pause
