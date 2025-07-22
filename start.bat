@echo off
REM Quick start script for Windows

echo 🚀 Starting Offline RAG Assistant...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup.py first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if models directory exists and has models
if not exist "models" (
    echo ⚠️  No models directory found.
    echo    Please create models/ directory and add a GGUF model file.
    pause
    exit /b 1
)

dir /b "models\*.gguf" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  No GGUF models found in models/ directory.
    echo    Please download a GGUF model file and place it in the models/ folder.
    echo    Then update the model path in rag.py
    pause
    exit /b 1
)

REM Start backend server
echo 🔧 Starting backend server...
cd chatbot
python rag_backend.py

echo ✅ RAG Assistant is running!
echo 📖 Open rag-index.html in your browser to start chatting with documents.
pause
