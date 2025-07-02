import os
from typing import Dict, Optional
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

class CredentialManager:
    """
    Manages all credentials and configuration for the AI Code Analysis Microservice.
    Uses environment variables for secure credential management.
    """
    
    def __init__(self):
        """Initialize the credential manager with environment variables."""
        self._load_credentials()
        logger.info("CredentialManager initialized successfully")
    
    def _load_credentials(self):
        """Load all credentials from environment variables."""
        # Git repository configuration
        self.git_repo_path = os.getenv('GIT_REPO_PATH', '/app/repo')
        
        # Database configuration
        self.db_type = os.getenv('DB_TYPE', 'postgresql')  # postgresql or mongodb
        self.db_credentials = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'user': os.getenv('DB_USER', 'user'),
            'password': os.getenv('DB_PASSWORD', 'password'),
            'database': os.getenv('DB_NAME', 'code_analysis'),
        }
        
        # MongoDB specific configuration
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.mongodb_db = os.getenv('MONGODB_DB', 'code_analysis')
        
        # API configuration
        self.api_host = os.getenv('API_HOST', '0.0.0.0')
        self.api_port = int(os.getenv('API_PORT', '5000'))
        self.api_debug = os.getenv('API_DEBUG', 'False').lower() == 'true'
        
        # Vector database configuration
        self.vector_dimension = int(os.getenv('VECTOR_DIMENSION', '768'))
        self.faiss_index_path = os.getenv('FAISS_INDEX_PATH', '/app/data/faiss_index')
        
        # Logging configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', '/app/logs/app.log')
        
        # External API keys (for future use)
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.github_token = os.getenv('GITHUB_TOKEN', '')
    
    def get_git_repo_path(self) -> str:
        """Get the local Git repository path."""
        return self.git_repo_path
    
    def get_db_credentials(self) -> Dict[str, str]:
        """Get database credentials."""
        return self.db_credentials.copy()
    
    def get_mongodb_config(self) -> Dict[str, str]:
        """Get MongoDB configuration."""
        return {
            'uri': self.mongodb_uri,
            'database': self.mongodb_db
        }
    
    def get_api_config(self) -> Dict[str, any]:
        """Get API configuration."""
        return {
            'host': self.api_host,
            'port': self.api_port,
            'debug': self.api_debug
        }
    
    def get_vector_config(self) -> Dict[str, any]:
        """Get vector database configuration."""
        return {
            'dimension': self.vector_dimension,
            'index_path': self.faiss_index_path
        }
    
    def get_logging_config(self) -> Dict[str, str]:
        """Get logging configuration."""
        return {
            'level': self.log_level,
            'file': self.log_file
        }
    
    def validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        required_vars = [
            self.git_repo_path,
            self.db_credentials['host'],
            self.db_credentials['user'],
            self.db_credentials['password'],
            self.db_credentials['database']
        ]
        
        missing_vars = [var for var in required_vars if not var]
        
        if missing_vars:
            logger.warning(f"Missing required environment variables: {missing_vars}")
            return False
        
        logger.info("All required credentials are present")
        return True
    
    def __str__(self) -> str:
        """String representation of the credential manager (without sensitive data)."""
        return f"CredentialManager(git_repo={self.git_repo_path}, db_type={self.db_type}, api_port={self.api_port})" 