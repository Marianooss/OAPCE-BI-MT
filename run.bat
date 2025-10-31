@echo off
REM OAPCE Multitrans - Run Script for Windows
REM This script starts the Streamlit application with optimized settings

echo 🚀 Starting OAPCE Multitrans...
echo 📊 Dashboard for Grupo OM
echo.
echo 🔧 Configuration:
echo    - Port: 5001
echo    - Address: 0.0.0.0
echo    - Headless: true
echo.
echo 🌐 Access your application at:
echo    http://localhost:5001
echo    http://127.0.0.1:5001
echo.
echo ⏳ Starting server...
echo.

REM Kill any existing Streamlit processes
taskkill /F /IM streamlit.exe 2>nul || echo No existing processes to kill

REM Start the application with optimized settings
streamlit run app.py --server.port 5001 --server.address 0.0.0.0 --server.headless true

pause
