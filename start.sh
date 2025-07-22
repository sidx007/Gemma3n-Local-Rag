#!/bin/bash
# Quick start script for Unix/Linux/macOS

echo "🚀 Starting Offline RAG Assistant..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.py first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if models directory exists and has models
if [ ! -d "models" ] || [ -z "$(ls -A models)" ]; then
    echo "⚠️  No models found in models/ directory."
    echo "   Please download a GGUF model file and place it in the models/ folder."
    echo "   Then update the model path in rag.py"
    exit 1
fi

# Start backend server
echo "🔧 Starting backend server..."
cd chatbot
python rag_backend.py

echo "✅ RAG Assistant is running!"
echo "📖 Open rag-index.html in your browser to start chatting with documents."
