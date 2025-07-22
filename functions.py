import sys
import os
from rag import LangChainRAG

def create_rag_system(files, topic, add_metadata=False, gemini_api_key=None):
    """Create a new RAG system with the specified files and topic."""
    rag = LangChainRAG(files, chunk_size=800, chunk_overlap=100, topic=topic, add_metadata=add_metadata, gemini_api_key=gemini_api_key)
    print("RAG system initialized.")
    return rag

def create_rag_project(project_name, file_paths, description="", category="General"):
    """Create a new RAG project with the given parameters."""
    try:
        # Validate file paths
        valid_files = []
        for file_path in file_paths:
            if os.path.exists(file_path) and file_path.lower().endswith('.pdf'):
                valid_files.append(file_path)
            else:
                print(f"Warning: File not found or not a PDF: {file_path}")
        
        if not valid_files:
            return {"error": "No valid PDF files provided"}
        
        # Normalize project name for consistent folder naming
        normalized_name = project_name.lower().replace(' ', '-')
        
        # Create the RAG system
        rag_system = create_rag_system(
            files=valid_files,
            topic=normalized_name,
            add_metadata=False,  # Set to True if you want to use metadata enhancement
            gemini_api_key=None   # Add your Gemini API key here if needed
        )
        
        # Create project folder structure
        project_folder = f"projects/{normalized_name}"
        os.makedirs(project_folder, exist_ok=True)
        
        # Save project metadata
        project_info = {
            "name": project_name,
            "description": description,
            "category": category,
            "files": valid_files,
            "created_date": str(os.path.getctime(project_folder) if os.path.exists(project_folder) else "unknown"),
            "document_count": len(valid_files)
        }
        
        print(f"Project '{project_name}' created successfully with {len(valid_files)} documents.")
        return {
            "success": True,
            "project_info": project_info,
            "rag_system": rag_system
        }
        
    except Exception as e:
        print(f"Error creating RAG project: {e}")
        return {"error": str(e)}

def query_rag_system(rag, query):
    """Query the RAG system and return the response."""
    try:
        return rag.query(query)
    except Exception as e:
        return f"Error processing query: {e}"

def list_project_files(project_folder):
    """List all files in a project folder."""
    try:
        if not os.path.exists(project_folder):
            return []
        
        files = []
        for file_name in os.listdir(project_folder):
            file_path = os.path.join(project_folder, file_name)
            if os.path.isfile(file_path):
                files.append({
                    "name": file_name,
                    "path": file_path,
                    "size": os.path.getsize(file_path)
                })
        return files
    except Exception as e:
        print(f"Error listing project files: {e}")
        return []