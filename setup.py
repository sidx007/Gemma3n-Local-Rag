#!/usr/bin/env python3
"""
Setup script for Offline RAG Assistant
Helps users get started quickly with the application
"""

import os
import sys
import subprocess
import platform

def print_banner():
    print("=" * 60)
    print("🤖 Offline RAG Assistant Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_venv():
    """Create virtual environment"""
    print("\n📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def get_activation_command():
    """Get the correct activation command for the OS"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Install Python dependencies"""
    print("\n📚 Installing dependencies...")
    
    # Get the correct pip path
    if platform.system() == "Windows":
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
    
    try:
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    if not os.path.exists(".env") and os.path.exists(".env.example"):
        print("\n📝 Creating .env file...")
        try:
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✅ .env file created from template")
        except Exception as e:
            print(f"⚠️  Could not create .env file: {e}")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = ["projects", "models"]
    
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ Created/verified directory: {dir_name}")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print(f"1. Activate virtual environment:")
    print(f"   {get_activation_command()}")
    print("\n2. Download an AI model (GGUF format) and place in models/ folder")
    print("   Recommended: Gemma 2B or Llama 3.1 8B quantized")
    print("\n3. Update model path in rag.py (line ~36)")
    print("\n4. Start the application:")
    print("   cd chatbot")
    print("   python rag_backend.py")
    print("\n5. Open rag-index.html in your browser")
    print("\n6. Create your first project and start chatting!")
    print("\n📖 See README.md for detailed instructions")
    print("🐛 Report issues: https://github.com/yourusername/offline-rag-assistant/issues")

def main():
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not os.path.exists("venv"):
        if not create_venv():
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Create directories
    create_directories()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
