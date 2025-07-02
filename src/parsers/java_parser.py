import tree_sitter
from tree_sitter import Language, Parser
from typing import Dict, List, Any
from pathlib import Path
from loguru import logger

from .base_parser import BaseParser

class JavaParser(BaseParser):
    """
    Java code parser using tree-sitter.
    Extracts methods, classes, imports, and complexity metrics from Java code.
    """
    
    def __init__(self):
        """Initialize the Java parser."""
        super().__init__("java")
    
    def _setup_language(self):
        """Setup tree-sitter Java language."""
        try:
            # Try to load the Java language
            self.language = Language('build/my-languages.so', 'java')
        except Exception:
            # If not found, try to build it
            logger.info("Building tree-sitter Java language...")
            Language.build_library(
                'build/my-languages.so',
                [
                    'vendor/tree-sitter-java'
                ]
            )
            self.language = Language('build/my-languages.so', 'java')
        
        self.parser.set_language(self.language)
        logger.info("Java language setup completed")
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a Java file and extract code features.
        
        Args:
            file_path: Path to the Java file to parse
            
        Returns:
            Dictionary containing parsed Java code features
        """
        if not self.validate_file(file_path):
            return {}
        
        try:
            with open(file_path, 'rb') as f:
                source_code = f.read()
            
            tree = self.parser.parse(source_code)
            
            result = {
                'file_path': file_path,
                'language': 'java',
                'methods': self.extract_methods(tree),
                'classes': self.extract_classes(tree),
                'imports': self.extract_imports(tree),
                'metrics': self.calculate_file_metrics(tree, source_code)
            }
            
            logger.debug(f"Parsed Java file: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing Java file {file_path}: {str(e)}")
            return {}
    
    def extract_methods(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract method definitions from Java AST."""
        methods = []
        source_code = tree.text
        
        # Query for method definitions
        query = self.language.query("""
            (method_declaration
                name: (identifier) @method.name
                parameters: (formal_parameters) @method.params
                body: (block) @method.body
            )
        """)
        
        captures = query.capture(tree.root_node)
        
        for capture in captures:
            if capture[1] == "method.name":
                method_name = self.get_node_text(capture[0], source_code)
                
                # Find corresponding parameters and body
                params_node = None
                body_node = None
                
                for other_capture in captures:
                    if other_capture[0].parent == capture[0].parent:
                        if other_capture[1] == "method.params":
                            params_node = other_capture[0]
                        elif other_capture[1] == "method.body":
                            body_node = other_capture[0]
                
                method_data = {
                    'name': method_name,
                    'position': self.get_node_position(capture[0]),
                    'parameters': self.extract_java_parameters(params_node, source_code) if params_node else [],
                    'complexity': self.calculate_complexity(capture[0].parent) if capture[0].parent else 1,
                    'body_text': self.get_node_text(body_node, source_code) if body_node else ""
                }
                
                methods.append(method_data)
        
        return methods
    
    def extract_classes(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract class definitions from Java AST."""
        classes = []
        source_code = tree.text
        
        # Query for class definitions
        query = self.language.query("""
            (class_declaration
                name: (identifier) @class.name
                body: (class_body) @class.body
            )
        """)
        
        captures = query.capture(tree.root_node)
        
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
        """Extract import statements from Java AST."""
        imports = []
        source_code = tree.text
        
        # Query for import statements
        query = self.language.query("""
            (import_declaration
                name: (scoped_identifier) @import.name
            )
        """)
        
        captures = query.capture(tree.root_node)
        
        for capture in captures:
            import_name = self.get_node_text(capture[0], source_code)
            import_data = {
                'name': import_name,
                'position': self.get_node_position(capture[0]),
                'text': f"import {import_name};"
            }
            imports.append(import_data)
        
        return imports
    
    def extract_java_parameters(self, params_node: tree_sitter.Node, source_code: bytes) -> List[Dict[str, str]]:
        """Extract parameter information from Java formal parameters."""
        if not params_node:
            return []
        
        parameters = []
        
        for child in params_node.children:
            if child.type == 'formal_parameter':
                param_name = None
                param_type = None
                
                for grandchild in child.children:
                    if grandchild.type == 'identifier':
                        param_name = self.get_node_text(grandchild, source_code)
                    elif grandchild.type in ['type_identifier', 'array_type', 'generic_type']:
                        param_type = self.get_node_text(grandchild, source_code)
                
                if param_name:
                    parameters.append({
                        'name': param_name,
                        'type': param_type or 'Object'
                    })
        
        return parameters
    
    def extract_class_methods(self, class_body: tree_sitter.Node, source_code: bytes) -> List[Dict[str, Any]]:
        """Extract methods from a Java class body."""
        methods = []
        
        for child in class_body.children:
            if child.type == 'method_declaration':
                method_name = None
                method_params = None
                
                for grandchild in child.children:
                    if grandchild.type == 'identifier':
                        method_name = self.get_node_text(grandchild, source_code)
                    elif grandchild.type == 'formal_parameters':
                        method_params = self.extract_java_parameters(grandchild, source_code)
                
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
        """Calculate various metrics for the Java file."""
        lines = source_code.decode('utf-8').split('\n')
        
        metrics = {
            'total_lines': len(lines),
            'code_lines': len([line for line in lines if line.strip() and not line.strip().startswith('//') and not line.strip().startswith('/*')]),
            'comment_lines': len([line for line in lines if line.strip().startswith('//') or line.strip().startswith('/*')]),
            'blank_lines': len([line for line in lines if not line.strip()]),
            'average_complexity': 0
        }
        
        # Calculate average complexity
        all_nodes = [tree.root_node]
        total_complexity = 0
        node_count = 0
        
        while all_nodes:
            node = all_nodes.pop(0)
            if node.type in ['method_declaration', 'class_declaration']:
                complexity = self.calculate_complexity(node)
                total_complexity += complexity
                node_count += 1
            
            all_nodes.extend(node.children)
        
        if node_count > 0:
            metrics['average_complexity'] = total_complexity / node_count
        
        return metrics
    
    def _get_default_file_patterns(self) -> List[str]:
        """Get default file patterns for Java files."""
        return ['*.java']         return metrics
    
    def _get_default_file_patterns(self) -> List[str]:
        """Get default file patterns for Java files."""
        return ['*.java']
        return metrics
    
    def _get_default_file_patterns(self) -> List[str]:
        """Get default file patterns for Java files."""
        return ['*.java']
