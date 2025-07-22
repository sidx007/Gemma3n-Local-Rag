@echo off
title RAG Chatbot Launcher

echo.
echo ╔══════════════════════════════════════════╗
echo ║        🤖 RAG Chatbot Launcher          ║
echo ║     Starting Backend and Frontend       ║
echo ╚══════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo � Running dependency test...
python test_backend.py
if errorlevel 1 (
    echo.
    echo ❌ Dependency test failed!
    echo Please install missing dependencies:
    echo   pip install flask flask-cors
    echo.
    pause
    exit /b 1
)

echo.
echo �📦 Starting RAG Backend Server...
echo.

REM Change to the chatbot directory
cd /d "%~dp0"

REM Start the backend server in a new window
start "RAG Backend Server" cmd /k "python rag_backend.py"

echo 🌐 Backend server starting on http://localhost:5001
echo ⏳ Please wait a few seconds for the server to fully start...
echo.

timeout /t 3 /nobreak >nul

echo 📋 Instructions:
echo   1. Backend server is starting (check the new window for status)
echo   2. Open rag-index.html in your browser
echo   3. Create or select a project to start chatting
echo.

echo 🚀 Opening frontend in your default browser...
start "" "%~dp0rag-index.html"

echo.
echo 📊 Backend Status:
echo   - Server URL: http://localhost:5001
echo   - API endpoints: /api/initialize-project, /api/chat-stream
echo   - Check the backend window for detailed logs
echo.

echo ⚠️  Important:
echo   - Make sure you have PDF files in the parent directory
echo   - If you see connection errors, wait for backend to fully start
echo   - Close the backend window to stop the server
echo.

pause
