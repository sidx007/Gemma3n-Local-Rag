from flask import Flask, request, jsonify, stream_template
from flask_cors import CORS
import json
import os
import sys
import time
import threading

# Add parent directory to path to find functions.py and rag.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from functions import create_rag_system, create_rag_project, query_rag_system, list_project_files
    print("✅ Successfully imported functions module")
except ImportError as e:
    print(f"❌ Failed to import functions module: {e}")
    print("Make sure functions.py is in the parent directory")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Global storage for active RAG systems
active_rag_systems = {}

@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'RAG Backend Server is running',
        'active_projects': len(active_rag_systems),
        'endpoints': [
            'GET /api/health',
            'POST /api/initialize-project/<id>',
            'POST /api/chat-stream/<id>',
            'GET /api/project-status/<id>'
        ]
    })

@app.route('/api/create-project', methods=['POST'])
def api_create_project():
    """Create a new RAG project with uploaded files"""
    try:
        data = request.get_json()
        
        project_name = data.get('name')
        description = data.get('description', '')
        category = data.get('category', 'General')
        file_paths = data.get('filePaths', [])
        
        if not project_name:
            return jsonify({'error': 'Project name is required'}), 400
        
        if not file_paths:
            return jsonify({'error': 'At least one PDF file is required'}), 400
        
        # Create the RAG project
        result = create_rag_project(project_name, file_paths, description, category)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'success': True,
            'message': f'Project "{project_name}" created successfully',
            'project_info': result['project_info']
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/initialize-project/<project_id>', methods=['POST'])
def api_initialize_project(project_id):
    """Initialize a RAG system for a specific project"""
    try:
        data = request.get_json()
        project_name = data.get('name', f'Project_{project_id}')
        file_paths = data.get('filePaths', [])
        
        # Check if RAG system is already initialized
        if project_id in active_rag_systems:
            return jsonify({
                'success': True,
                'message': 'RAG system already initialized',
                'cached': True,
                'file_count': len(active_rag_systems[project_id]['files'])
            })
        
        # Use default files if no file paths provided
        default_files = [
            os.path.join('..', 'p.pdf'),
            os.path.join('..', 'P2.pdf')
        ]
        
        # Find existing PDF files
        files_to_use = []
        if file_paths:
            # Use provided file paths
            for file_path in file_paths:
                full_path = os.path.join('..', file_path)
                if os.path.exists(full_path):
                    files_to_use.append(full_path)
        else:
            # Use default files that exist
            for default_file in default_files:
                if os.path.exists(default_file):
                    files_to_use.append(default_file)
        
        if not files_to_use:
            return jsonify({
                'error': 'No PDF files found. Please make sure PDF files exist in the project directory.',
                'checked_paths': default_files + [os.path.join('..', fp) for fp in file_paths] if file_paths else default_files
            }), 400
        
        print(f"🚀 Initializing RAG system for project: {project_name}")
        print(f"📁 Using files: {files_to_use}")
        
        # Create the RAG system - use project_id (folder name) for consistency
        rag_system = create_rag_system(
            files=files_to_use,
            topic=project_id,  # Use project_id instead of project_name for folder consistency
            add_metadata=False
        )
        
        # Store the RAG system
        active_rag_systems[project_id] = {
            'rag_system': rag_system,
            'project_name': project_name,
            'files': files_to_use,
            'initialized_at': time.time()
        }
        
        print(f"✅ RAG system initialized successfully for: {project_name}")
        
        return jsonify({
            'success': True,
            'message': f'RAG system initialized for project "{project_name}"',
            'file_count': len(files_to_use),
            'files_used': [os.path.basename(f) for f in files_to_use]
        })
        
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        return jsonify({'error': f'Failed to initialize RAG system: {str(e)}'}), 500

@app.route('/api/chat/<project_id>', methods=['POST'])
def api_chat(project_id):
    """Handle chat query for a specific project"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Check if RAG system is initialized
        if project_id not in active_rag_systems:
            return jsonify({'error': 'RAG system not initialized for this project'}), 400
        
        rag_info = active_rag_systems[project_id]
        rag_system = rag_info['rag_system']
        
        # Query the RAG system (non-streaming for now)
        response = query_rag_system(rag_system, query)
        
        return jsonify({
            'success': True,
            'response': response,
            'project_name': rag_info['project_name']
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing query: {str(e)}'}), 500

@app.route('/api/chat-stream/<project_id>', methods=['POST'])
def api_chat_stream(project_id):
    """Handle streaming chat query for a specific project"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Check if RAG system is initialized
        if project_id not in active_rag_systems:
            return jsonify({'error': 'RAG system not initialized for this project'}), 400
        
        rag_info = active_rag_systems[project_id]
        rag_system = rag_info['rag_system']
        
        def generate():
            try:
                # Send initial metadata
                yield f"data: {json.dumps({'type': 'start', 'project': rag_info['project_name']})}\n\n"
                
                # Query the RAG system and stream the response
                for chunk in rag_system.query(query):
                    if chunk is not None and chunk.strip():
                        yield f"data: {json.dumps({'type': 'chunk', 'content': str(chunk)})}\n\n"
                
                # Send end signal
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return app.response_class(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )
        
    except Exception as e:
        return jsonify({'error': f'Error processing streaming query: {str(e)}'}), 500

@app.route('/api/project-status/<project_id>')
def api_project_status(project_id):
    """Get status of a RAG project"""
    if project_id in active_rag_systems:
        rag_info = active_rag_systems[project_id]
        return jsonify({
            'initialized': True,
            'project_name': rag_info['project_name'],
            'file_count': len(rag_info['files']),
            'initialized_at': rag_info['initialized_at']
        })
    else:
        return jsonify({
            'initialized': False,
            'message': 'RAG system not initialized for this project'
        })

@app.route('/api/list-projects')
def api_list_projects():
    """List all available projects from the projects folder"""
    try:
        projects = []
        projects_folder = 'projects'
        
        if os.path.exists(projects_folder):
            for folder_name in os.listdir(projects_folder):
                folder_path = os.path.join(projects_folder, folder_name)
                if os.path.isdir(folder_path):
                    files = list_project_files(folder_path)
                    projects.append({
                        'id': folder_name,
                        'name': folder_name.replace('-', ' ').title(),
                        'folder': folder_name,
                        'files': files,
                        'file_count': len(files)
                    })
        
        return jsonify({'projects': projects})
        
    except Exception as e:
        return jsonify({'error': f'Error listing projects: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting RAG Backend Server...")
    print("Available endpoints:")
    print("  POST /api/create-project - Create new RAG project")
    print("  POST /api/initialize-project/<id> - Initialize RAG system")
    print("  POST /api/chat/<id> - Chat with project (non-streaming)")
    print("  POST /api/chat-stream/<id> - Chat with project (streaming)")
    print("  GET /api/project-status/<id> - Get project status")
    print("  GET /api/list-projects - List all projects")
    print("\nServer running on http://localhost:5001")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
