#!/usr/bin/env python3
"""
Setup script for AI Code Analysis Microservice.
This script helps initialize the project and test components.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = [
        'logs',
        'data',
        'repo',
        'build',
        'vendor'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies."""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def setup_tree_sitter():
    """Setup tree-sitter languages."""
    print("🌳 Setting up tree-sitter languages...")
    
    # Create vendor directory if it doesn't exist
    vendor_dir = Path("vendor")
    vendor_dir.mkdir(exist_ok=True)
    
    # Clone tree-sitter repositories
    languages = {
        'python': 'https://github.com/tree-sitter/tree-sitter-python.git',
        'go': 'https://github.com/tree-sitter/tree-sitter-go.git',
        'java': 'https://github.com/tree-sitter/tree-sitter-java.git'
    }
    
    for lang, repo in languages.items():
        lang_dir = vendor_dir / f"tree-sitter-{lang}"
        if not lang_dir.exists():
            print(f"📥 Cloning tree-sitter-{lang}...")
            run_command(f"git clone {repo} {lang_dir}", f"Cloning tree-sitter-{lang}")
        else:
            print(f"📁 tree-sitter-{lang} already exists")
    
    # Build language library
    print("🔨 Building tree-sitter language library...")
    try:
        from tree_sitter import Language
        
        # Get vendor paths
        vendor_paths = [str(vendor_dir / f"tree-sitter-{lang}") for lang in languages.keys()]
        
        # Build library
        Language.build_library('build/my-languages.so', vendor_paths)
        print("✅ Tree-sitter language library built successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to build tree-sitter library: {e}")
        return False

def test_components():
    """Test basic components."""
    print("🧪 Testing components...")
    
    try:
        # Add current directory to Python path
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        # Test imports
        from src.config.credential_manager import CredentialManager
        from src.parsers.parser_factory import ParserFactory
        from src.vectorization.embedding_manager import EmbeddingManager
        from src.utils.logger import get_logger
        
        print("✅ All imports successful")
        
        # Test credential manager
        cred_manager = CredentialManager()
        print("✅ Credential manager initialized")
        
        # Test parser factory
        parser_factory = ParserFactory()
        languages = parser_factory.get_supported_languages()
        print(f"✅ Parser factory initialized with languages: {languages}")
        
        # Test logger
        logger = get_logger()
        print("✅ Logger initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def create_sample_files():
    """Create sample files for testing."""
    print("📝 Creating sample files...")
    
    # Sample Python file
    python_code = '''
def hello_world():
    """Simple hello world function."""
    print("Hello, World!")

class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
'''
    
    sample_file = Path("repo/sample.py")
    sample_file.parent.mkdir(exist_ok=True)
    sample_file.write_text(python_code)
    print(f"✅ Created sample file: {sample_file}")
    
    # Sample Go file
    go_code = '''
package main

import "fmt"

func helloWorld() {
    fmt.Println("Hello, World!")
}

type Calculator struct {
    value int
}

func (c *Calculator) Add(a int) int {
    return c.value + a
}
'''
    
    sample_file = Path("repo/sample.go")
    sample_file.write_text(go_code)
    print(f"✅ Created sample file: {sample_file}")

def main():
    """Main setup function."""
    print("🚀 AI Code Analysis Microservice Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup tree-sitter
    if not setup_tree_sitter():
        print("❌ Failed to setup tree-sitter")
        sys.exit(1)
    
    # Test components
    if not test_components():
        print("❌ Component tests failed")
        sys.exit(1)
    
    # Create sample files
    create_sample_files()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and configure your settings")
    print("2. Run 'docker-compose up --build' to start the service")
    print("3. Or run 'python app.py' for local development")
    print("4. Visit http://localhost:5000/docs for API documentation")

if __name__ == "__main__":
    main() 