# 🤖 RAG Chatbot Interface

A modern web interface for interacting with RAG (Retrieval-Augmented Generation) systems.

## 🚀 Quick Start

1. **Run the launcher**:
   ```bash
   start_chatbot.bat
   ```

2. **Open the frontend**:
   - Open `rag-index.html` in your web browser
   - Or navigate to the file path shown in the launcher

3. **Create a project**:
   - Click "Create New Project"
   - Select PDF documents
   - Fill in project details

4. **Start chatting**:
   - Click on a project to open the chat interface
   - Wait for RAG system initialization
   - Ask questions about your documents!

## 📁 Files Overview

- `rag-index.html` - Main web interface
- `rag-app.js` - Frontend JavaScript logic
- `rag-style.css` - Styling and themes
- `rag_backend.py` - Flask backend server
- `start_chatbot.bat` - Easy launcher script

## 🔧 Backend API

The backend runs on `http://localhost:5001` with these endpoints:

- `POST /api/initialize-project/<id>` - Initialize RAG system for project
- `POST /api/chat-stream/<id>` - Stream chat responses
- `GET /api/project-status/<id>` - Check project initialization status
- `GET /api/list-projects` - List available projects

## 🎯 Features

- **Modern UI**: Glassmorphism design with light/dark themes
- **Real-time Streaming**: Token-by-token response streaming
- **Project Management**: Create and organize RAG projects
- **File Selection**: Multi-PDF document selection
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: Robust error management and user feedback

## 🛠️ Requirements

- Python 3.8+
- Required packages (install via `pip install -r requirements.txt`):
  - flask
  - flask-cors
  - langchain
  - langchain-community
  - llama-cpp-python
  - sentence-transformers
  - faiss-cpu
  - pypdf

## 🔍 How It Works

1. **Project Creation**: Select PDF files and create a RAG project
2. **RAG Initialization**: Backend creates embeddings and vector store
3. **Chat Interface**: Stream responses from the RAG system
4. **Document Retrieval**: Finds relevant document chunks for queries
5. **LLM Generation**: Generates contextual responses using retrieved content

## 🎨 Customization

- **Themes**: Toggle between light and dark modes
- **Styling**: Modify `rag-style.css` for custom appearance
- **Backend**: Adjust `rag_backend.py` for different models or settings
- **UI**: Customize `rag-index.html` and `rag-app.js` for features

## 🐛 Troubleshooting

### Backend Issues
- Ensure Python and required packages are installed
- Check that port 5001 is available
- Verify PDF files are accessible

### Frontend Issues
- Use a modern browser (Chrome, Firefox, Safari, Edge)
- Check browser console for JavaScript errors
- Ensure backend server is running before using chat

### RAG Issues
- Verify PDF files contain extractable text
- Check model files exist and are accessible
- Monitor backend console for initialization errors

## 📞 Support

- Check backend console output for detailed error messages
- Use browser developer tools to inspect network requests
- Ensure all file paths are correct and accessible

---

**Ready to chat with your documents!** 🚀
