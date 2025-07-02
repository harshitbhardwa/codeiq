import sys
import os
from pathlib import Path
from loguru import logger
from typing import Dict, Any

class LoggerSetup:
    """
    Comprehensive logging setup for the AI Code Analysis Microservice.
    Supports multiple log levels, file rotation, and structured logging.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize logger with configuration."""
        self.config = config
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure the logger with file and console outputs."""
        # Remove default logger
        logger.remove()
        
        # Create logs directory if it doesn't exist
        log_file = self.config.get('file', '/app/logs/app.log')
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Console logging
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=self.config.get('level', 'INFO'),
            colorize=True
        )
        
        # File logging with rotation
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=self.config.get('level', 'INFO'),
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # Error file logging
        error_log_file = str(log_dir / "error.log")
        logger.add(
            error_log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="5 MB",
            retention="60 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        logger.info("Logger setup completed successfully")
    
    def log_api_request(self, method: str, path: str, status_code: int, duration: float):
        """Log API request details."""
        logger.info(f"API Request: {method} {path} - Status: {status_code} - Duration: {duration:.3f}s")
    
    def log_code_analysis(self, file_path: str, language: str, functions_count: int, classes_count: int):
        """Log code analysis results."""
        logger.info(f"Code Analysis: {file_path} ({language}) - Functions: {functions_count}, Classes: {classes_count}")
    
    def log_database_operation(self, operation: str, table: str, duration: float):
        """Log database operations."""
        logger.info(f"Database: {operation} on {table} - Duration: {duration:.3f}s")
    
    def log_vector_operation(self, operation: str, vectors_count: int, duration: float):
        """Log vector database operations."""
        logger.info(f"Vector DB: {operation} - Vectors: {vectors_count} - Duration: {duration:.3f}s")
    
    def log_error(self, error: Exception, context: str = ""):
        """Log errors with context."""
        logger.error(f"Error in {context}: {str(error)}")
    
    def log_warning(self, message: str, context: str = ""):
        """Log warnings with context."""
        logger.warning(f"Warning in {context}: {message}")
    
    def log_debug(self, message: str, context: str = ""):
        """Log debug messages with context."""
        logger.debug(f"Debug in {context}: {message}")

# Global logger instance
def get_logger() -> LoggerSetup:
    """Get the global logger instance."""
    from src.config.credential_manager import CredentialManager
    
    cred_manager = CredentialManager()
    logging_config = cred_manager.get_logging_config()
    
    return LoggerSetup(logging_config) 