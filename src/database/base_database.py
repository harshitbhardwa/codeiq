from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from loguru import logger

class BaseDatabase(ABC):
    """
    Base class for database operations.
    Defines the interface that all database implementations must implement.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the database with configuration."""
        self.config = config
        self.connected = False
        logger.info(f"Initializing {self.__class__.__name__}")
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the database."""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from the database."""
        pass
    
    @abstractmethod
    def store_analysis_result(self, analysis_data: Dict[str, Any]) -> bool:
        """Store code analysis results."""
        pass
    
    @abstractmethod
    def get_analysis_result(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Retrieve code analysis results for a file."""
        pass
    
    @abstractmethod
    def store_alert_data(self, alert_data: Dict[str, Any]) -> bool:
        """Store alert data."""
        pass
    
    @abstractmethod
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve alert history."""
        pass
    
    @abstractmethod
    def search_analysis_results(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search analysis results based on criteria."""
        pass
    
    @abstractmethod
    def update_analysis_result(self, file_path: str, update_data: Dict[str, Any]) -> bool:
        """Update existing analysis results."""
        pass
    
    @abstractmethod
    def delete_analysis_result(self, file_path: str) -> bool:
        """Delete analysis results for a file."""
        pass
    
    @abstractmethod
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        pass
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.connected
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect() 