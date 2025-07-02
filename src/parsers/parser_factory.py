from typing import Dict, Type, Optional
from loguru import logger

from .base_parser import BaseParser
from .python_parser import PythonParser
from .go_parser import GoParser
from .java_parser import JavaParser

class ParserFactory:
    """
    Factory class for creating language-specific parsers.
    Manages the creation and caching of parsers for different programming languages.
    """
    
    def __init__(self):
        """Initialize the parser factory."""
        self._parsers: Dict[str, BaseParser] = {}
        self._supported_languages = {
            'python': PythonParser,
            'py': PythonParser,
            'go': GoParser,
            'golang': GoParser,
            'java': JavaParser
        }
        logger.info("ParserFactory initialized")
    
    def get_parser(self, language: str) -> Optional[BaseParser]:
        """
        Get a parser for the specified language.
        
        Args:
            language: Programming language name or file extension
            
        Returns:
            Parser instance for the language, or None if not supported
        """
        language_lower = language.lower()
        
        # Check if we already have a cached parser
        if language_lower in self._parsers:
            return self._parsers[language_lower]
        
        # Check if language is supported
        if language_lower not in self._supported_languages:
            logger.warning(f"Unsupported language: {language}")
            return None
        
        try:
            # Create new parser instance
            parser_class = self._supported_languages[language_lower]
            parser = parser_class()
            
            # Cache the parser
            self._parsers[language_lower] = parser
            
            logger.info(f"Created parser for language: {language}")
            return parser
            
        except Exception as e:
            logger.error(f"Error creating parser for {language}: {str(e)}")
            return None
    
    def get_parser_by_file_extension(self, file_path: str) -> Optional[BaseParser]:
        """
        Get a parser based on file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Parser instance for the file type, or None if not supported
        """
        from pathlib import Path
        
        file_extension = Path(file_path).suffix.lower()
        if file_extension.startswith('.'):
            file_extension = file_extension[1:]  # Remove the dot
        
        return self.get_parser(file_extension)
    
    def get_supported_languages(self) -> list:
        """Get list of supported programming languages."""
        return list(self._supported_languages.keys())
    
    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported."""
        return language.lower() in self._supported_languages
    
    def clear_cache(self):
        """Clear the parser cache."""
        self._parsers.clear()
        logger.info("Parser cache cleared")
    
    def get_parser_info(self) -> Dict[str, str]:
        """Get information about available parsers."""
        return {
            language: parser_class.__name__
            for language, parser_class in self._supported_languages.items()
        } 