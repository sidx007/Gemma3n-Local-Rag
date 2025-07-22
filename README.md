# 🤖 Offline RAG Assistant

A modern, offline Retrieval-Augmented Generation (RAG) application that allows you to chat with your PDF documents using local AI models. Built with Python, Flask, and vanilla JavaScript with a beautiful glassmorphism UI.

![RAG Assistant Screenshot](https://img.shields.io/badge/RAG-Assistant-blue?style=for-the-badge&logo=ai&logoColor=white)

## ✨ Features

- **🔒 Fully Offline**: No data leaves your machine - complete privacy
- **📚 Multi-Document RAG**: Process multiple PDF documents simultaneously
- **💬 Real-time Streaming**: Live streaming responses from local AI models
- **🎨 Modern UI**: Beautiful glassmorphism design with dark/light themes
- **📁 Project Management**: Organize documents into projects
- **⚡ Fast Retrieval**: Optimized vector search with FAISS
- **🧠 Local LLMs**: Uses llama.cpp for fast local inference
- **🔍 Smart Chunking**: Intelligent document splitting with metadata
- **📱 Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Frontend      │───▶│    Flask     │───▶│   RAG System    │
│   (HTML/CSS/JS) │    │   Backend    │    │   (Python)      │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │                       │
                              ▼                       ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Project       │    │   Streaming  │    │   Vector Store  │
│   Management    │    │   Chat API   │    │   (FAISS)       │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Windows/Linux/macOS
- At least 4GB RAM (8GB recommended for larger models)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/offline-rag-assistant.git
   cd offline-rag-assistant
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\\Scripts\\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download AI Models**
   - Place your GGUF model file in `models/` directory
   - Update the model path in `rag.py` (line 36)
   ```python
   model_path = "models/your-model.gguf"
   ```

5. **Start the application**
   ```bash
   cd chatbot
   ./start_chatbot.bat  # Windows
   # or
   python rag_backend.py  # Direct start
   ```

6. **Open your browser**
   - Navigate to the displayed file path (usually `rag-index.html`)
   - Start creating projects and chatting with your documents!

## 📖 Usage Guide

### Creating a New Project

1. Click **"Create New Project"**
2. Enter project name and description
3. Select one or more PDF files
4. Choose a category
5. Click **"Create Project"**

The system will automatically:
- Process your PDFs
- Create vector embeddings
- Set up the RAG pipeline
- Save everything locally in the `projects/` folder

### Chatting with Documents

1. Click on any project card
2. Wait for the RAG system to initialize
3. Start asking questions about your documents
4. Get real-time streaming responses

### Project Management

- **View Projects**: All projects are displayed on the home page
- **Filter Projects**: Use category filters or search
- **Delete Projects**: Click the delete button on any project card
- **Refresh Projects**: Click refresh to load projects from backend

## 🔧 Configuration

### Model Configuration

Edit `rag.py` to configure your model:

```python
# Model settings
model_path = "models/your-model.gguf"
prompt_tokens = 2048
n_threads = 4  # Adjust based on your CPU

# Embeddings model
embeddings_model = "C:\\models\\static-mrl"  # Update path
```

### Backend Configuration

Edit `rag_backend.py` for server settings:

```python
# Server configuration
HOST = '0.0.0.0'
PORT = 5001
DEBUG = True
```

### UI Themes

The application supports both dark and light themes. The default theme is dark mode, but users can toggle using the theme button.

## 📁 Project Structure

```
offline-rag-assistant/
├── chatbot/                 # Web interface
│   ├── rag-index.html      # Main HTML file
│   ├── rag-app.js          # Frontend JavaScript
│   ├── rag-style.css       # Styling
│   ├── rag_backend.py      # Flask backend
│   └── start_chatbot.bat   # Startup script
├── projects/               # Generated project folders
├── models/                 # AI model files (not included)
├── rag.py                  # Core RAG implementation
├── functions.py            # RAG utility functions
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔌 API Endpoints

The Flask backend provides these endpoints:

- `GET /api/health` - Health check
- `POST /api/create-project` - Create new RAG project
- `POST /api/initialize-project/<id>` - Initialize RAG system
- `POST /api/chat-stream/<id>` - Streaming chat endpoint
- `GET /api/list-projects` - List all projects
- `GET /api/project-status/<id>` - Get project status

## 🛠️ Advanced Features

### Custom Embeddings

The system uses HuggingFace embeddings by default. To use custom embeddings:

```python
# In rag.py
self.embeddings = HuggingFaceEmbeddings(
    model_name="your-custom-embedding-model"
)
```

### Metadata Enhancement

Enable metadata enhancement for better retrieval:

```python
# In functions.py
add_metadata=True,
gemini_api_key="your-gemini-key"  # Optional
```

### Custom Chunking

Adjust document chunking parameters:

```python
chunk_size = 800      # Characters per chunk
chunk_overlap = 100   # Overlap between chunks
```

## 🔒 Privacy & Security

- **100% Offline**: All processing happens locally
- **No Data Collection**: No telemetry or analytics
- **Local Storage**: Documents and embeddings stored locally
- **API Key Safety**: No hardcoded API keys in the codebase

## 🐛 Troubleshooting

### Common Issues

**Backend Connection Error**
```bash
# Check if backend is running
python test_backend.py

# Install missing dependencies
pip install flask flask-cors
```

**Model Loading Issues**
- Ensure model path is correct in `rag.py`
- Check available RAM (models require 4-8GB)
- Verify model format (GGUF required)

**PDF Processing Errors**
- Ensure PDFs are not encrypted
- Check file permissions
- Try with smaller PDF files first

**UI Not Loading**
- Check browser console for errors
- Ensure all files are in correct directories
- Try refreshing the page

### Performance Optimization

1. **Reduce Model Size**: Use quantized models (Q4, Q5)
2. **Adjust Threads**: Set `n_threads` to match CPU cores
3. **Optimize Chunks**: Tune `chunk_size` based on content
4. **Limit Context**: Reduce `n_ctx` for faster responses

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Format code
black .
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) - RAG framework
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - Local inference
- [FAISS](https://github.com/facebookresearch/faiss) - Vector similarity search
- [HuggingFace](https://huggingface.co/) - Embeddings models
- [Flask](https://flask.palletsprojects.com/) - Backend framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/offline-rag-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/offline-rag-assistant/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/offline-rag-assistant/wiki)

---

**⭐ If you find this project helpful, please give it a star! ⭐**

Built with ❤️ for privacy-focused AI enthusiasts
