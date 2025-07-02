import tree_sitter
from tree_sitter import Language, Parser
from typing import Dict, List, Any
from pathlib import Path
from loguru import logger

from .base_parser import BaseParser

class PythonParser(BaseParser):
    """
    Python code parser using tree-sitter.
    Extracts functions, classes, imports, and complexity metrics from Python code.
    """
    
    def __init__(self):
        """Initialize the Python parser."""
        super().__init__("python")
    
    def _setup_language(self):
        """Setup tree-sitter Python language."""
        try:
            # Try to load the Python language
            self.language = Language('build/my-languages.so', 'python')
        except Exception:
            # If not found, try to build it
            logger.info("Building tree-sitter Python language...")
            Language.build_library(
                'build/my-languages.so',
                [
                    'vendor/tree-sitter-python'
                ]
            )
            self.language = Language('build/my-languages.so', 'python')
        
        self.parser.set_language(self.language)
        logger.info("Python language setup completed")
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a Python file and extract code features.
        
        Args:
            file_path: Path to the Python file to parse
            
        Returns:
            Dictionary containing parsed Python code features
        """
        if not self.validate_file(file_path):
            return {}
        
        try:
            with open(file_path, 'rb') as f:
                source_code = f.read()
            
            tree = self.parser.parse(source_code)
            
            result = {
                'file_path': file_path,
                'language': 'python',
                'functions': self.extract_functions(tree),
                'classes': self.extract_classes(tree),
                'imports': self.extract_imports(tree),
                'metrics': self.calculate_file_metrics(tree, source_code)
            }
            
            logger.debug(f"Parsed Python file: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing Python file {file_path}: {str(e)}")
            return {}
    
    def extract_functions(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract function definitions from Python AST."""
        functions = []
        source_code = tree.text
        
        # Query for function definitions
        query = self.language.query("""
            (function_definition
                name: (identifier) @function.name
                parameters: (parameters) @function.params
                body: (block) @function.body
            )
        """)
        
        captures = query.captures(tree.root_node)
        
        for capture in captures:
            if capture[1] == "function.name":
                function_name = self.get_node_text(capture[0], source_code)
                
                # Find corresponding parameters and body
                params_node = None
                body_node = None
                
                for other_capture in captures:
                    if other_capture[0].parent == capture[0].parent:
                        if other_capture[1] == "function.params":
                            params_node = other_capture[0]
                        elif other_capture[1] == "function.body":
                            body_node = other_capture[0]
                
                function_data = {
                    'name': function_name,
                    'position': self.get_node_position(capture[0]),
                    'parameters': self.extract_parameters(params_node, source_code) if params_node else [],
                    'complexity': self.calculate_complexity(capture[0].parent) if capture[0].parent else 1,
                    'body_text': self.get_node_text(body_node, source_code) if body_node else ""
                }
                
                functions.append(function_data)
        
        return functions
    
    def extract_classes(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract class definitions from Python AST."""
        classes = []
        source_code = tree.text
        
        # Query for class definitions
        query = self.language.query("""
            (class_definition
                name: (identifier) @class.name
                body: (block) @class.body
            )
        """)
        
        captures = query.captures(tree.root_node)
        
        for capture in captures:
            if capture[1] == "class.name":
                class_name = self.get_node_text(capture[0], source_code)
                
                # Find corresponding body
                body_node = None
                for other_capture in captures:
                    if other_capture[0].parent == capture[0].parent and other_capture[1] == "class.body":
                        body_node = other_capture[0]
                        break
                
                # Extract methods from class body
                methods = []
                if body_node:
                    methods = self.extract_class_methods(body_node, source_code)
                
                class_data = {
                    'name': class_name,
                    'position': self.get_node_position(capture[0]),
                    'methods': methods,
                    'complexity': self.calculate_complexity(capture[0].parent) if capture[0].parent else 1,
                    'body_text': self.get_node_text(body_node, source_code) if body_node else ""
                }
                
                classes.append(class_data)
        
        return classes
    
    def extract_imports(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract import statements from Python AST."""
        imports = []
        source_code = tree.text
        
        # Query for import statements
        query = self.language.query("""
            (import_statement
                name: (dotted_name) @import.name
            )
            (import_from_statement
                module_name: (dotted_name) @import.module
                name: (dotted_name) @import.name
            )
        """)
        
        captures = query.captures(tree.root_node)
        
        for capture in captures:
            import_text = self.get_node_text(capture[0], source_code)
            import_data = {
                'text': import_text,
                'position': self.get_node_position(capture[0]),
                'type': 'import' if capture[1] == 'import' else 'import_from'
            }
            imports.append(import_data)
        
        return imports
    
    def extract_parameters(self, params_node: tree_sitter.Node, source_code: bytes) -> List[str]:
        """Extract parameter names from function parameters."""
        if not params_node:
            return []
        
        parameters = []
        for child in params_node.children:
            if child.type == 'identifier':
                parameters.append(self.get_node_text(child, source_code))
            elif child.type == 'typed_parameter':
                # Handle typed parameters
                for grandchild in child.children:
                    if grandchild.type == 'identifier':
                        parameters.append(self.get_node_text(grandchild, source_code))
                        break
        
        return parameters
    
    def extract_class_methods(self, class_body: tree_sitter.Node, source_code: bytes) -> List[Dict[str, Any]]:
        """Extract methods from a class body."""
        methods = []
        
        for child in class_body.children:
            if child.type == 'function_definition':
                method_name = None
                method_params = None
                
                for grandchild in child.children:
                    if grandchild.type == 'identifier':
                        method_name = self.get_node_text(grandchild, source_code)
                    elif grandchild.type == 'parameters':
                        method_params = self.extract_parameters(grandchild, source_code)
                
                if method_name:
                    method_data = {
                        'name': method_name,
                        'position': self.get_node_position(child),
                        'parameters': method_params or [],
                        'complexity': self.calculate_complexity(child),
                        'body_text': self.get_node_text(child, source_code)
                    }
                    methods.append(method_data)
        
        return methods
    
    def calculate_file_metrics(self, tree: tree_sitter.Tree, source_code: bytes) -> Dict[str, Any]:
        """Calculate various metrics for the Python file."""
        lines = source_code.decode('utf-8').split('\n')
        
        metrics = {
            'total_lines': len(lines),
            'code_lines': len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            'comment_lines': len([line for line in lines if line.strip().startswith('#')]),
            'blank_lines': len([line for line in lines if not line.strip()]),
            'average_complexity': 0
        }
        
        # Calculate average complexity
        all_nodes = [tree.root_node]
        total_complexity = 0
        node_count = 0
        
        while all_nodes:
            node = all_nodes.pop(0)
            if node.type in ['function_definition', 'class_definition']:
                complexity = self.calculate_complexity(node)
                total_complexity += complexity
                node_count += 1
            
            all_nodes.extend(node.children)
        
        if node_count > 0:
            metrics['average_complexity'] = total_complexity / node_count
        
        return metrics
    
    def _get_default_file_patterns(self) -> List[str]:
        """Get default file patterns for Python files."""
        return ['*.py'] 