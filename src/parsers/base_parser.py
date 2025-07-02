from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path
import tree_sitter
from loguru import logger

class BaseParser(ABC):
    """
    Base class for all code parsers.
    Defines the interface that all language-specific parsers must implement.
    """
    
    def __init__(self, language: str):
        """Initialize the base parser with language specification."""
        self.language = language
        self.parser = tree_sitter.Parser()
        self._setup_language()
        logger.info(f"Initialized {language} parser")
    
    @abstractmethod
    def _setup_language(self):
        """Setup the tree-sitter language for the specific programming language."""
        pass
    
    @abstractmethod
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a single file and extract code features.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Dictionary containing parsed code features
        """
        pass
    
    @abstractmethod
    def extract_functions(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract function definitions from the AST."""
        pass
    
    @abstractmethod
    def extract_classes(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract class definitions from the AST."""
        pass
    
    @abstractmethod
    def extract_imports(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract import statements from the AST."""
        pass
    
    def calculate_complexity(self, node: tree_sitter.Node) -> int:
        """
        Calculate cyclomatic complexity for a code block.
        
        Args:
            node: Tree-sitter node to analyze
            
        Returns:
            Complexity score
        """
        complexity = 1  # Base complexity
        
        # Count decision points
        decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'case', 'catch', 'except']
        
        def count_decisions(n: tree_sitter.Node):
            nonlocal complexity
            if n.type in decision_keywords:
                complexity += 1
            for child in n.children:
                count_decisions(child)
        
        count_decisions(node)
        return complexity
    
    def get_node_text(self, node: tree_sitter.Node, source_code: bytes) -> str:
        """Extract text content from a tree-sitter node."""
        return source_code[node.start_byte:node.end_byte].decode('utf-8')
    
    def get_node_position(self, node: tree_sitter.Node) -> Dict[str, int]:
        """Get the position information for a node."""
        return {
            'start_line': node.start_point[0],
            'start_column': node.start_point[1],
            'end_line': node.end_point[0],
            'end_column': node.end_point[1]
        }
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate if the file can be parsed by this parser.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file can be parsed, False otherwise
        """
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return False
        
        if not path.is_file():
            logger.warning(f"Path is not a file: {file_path}")
            return False
        
        return True
    
    def parse_repository(self, repo_path: str, file_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Parse all relevant files in a repository.
        
        Args:
            repo_path: Path to the repository
            file_patterns: List of file patterns to include (e.g., ['*.py', '*.go'])
            
        Returns:
            Dictionary containing parsed results for all files
        """
        from pathlib import Path
        import glob
        
        results = {
            'repository': repo_path,
            'language': self.language,
            'files': [],
            'summary': {
                'total_files': 0,
                'total_functions': 0,
                'total_classes': 0,
                'total_imports': 0
            }
        }
        
        repo_path_obj = Path(repo_path)
        if not repo_path_obj.exists():
            logger.error(f"Repository path does not exist: {repo_path}")
            return results
        
        # Default file patterns if none provided
        if file_patterns is None:
            file_patterns = self._get_default_file_patterns()
        
        # Find all matching files
        all_files = []
        for pattern in file_patterns:
            pattern_path = repo_path_obj / "**" / pattern
            all_files.extend(glob.glob(str(pattern_path), recursive=True))
        
        logger.info(f"Found {len(all_files)} files to parse in {repo_path}")
        
        # Parse each file
        for file_path in all_files:
            try:
                file_result = self.parse_file(file_path)
                if file_result:
                    results['files'].append(file_result)
                    results['summary']['total_files'] += 1
                    results['summary']['total_functions'] += len(file_result.get('functions', []))
                    results['summary']['total_classes'] += len(file_result.get('classes', []))
                    results['summary']['total_imports'] += len(file_result.get('imports', []))
            except Exception as e:
                logger.error(f"Error parsing file {file_path}: {str(e)}")
        
        logger.info(f"Successfully parsed {results['summary']['total_files']} files")
        return results
    
    @abstractmethod
    def _get_default_file_patterns(self) -> List[str]:
        """Get default file patterns for this language."""
        pass 