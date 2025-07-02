import tree_sitter
from tree_sitter import Language, Parser
from typing import Dict, List, Any
from pathlib import Path
from loguru import logger
import re

from .base_parser import BaseParser

class JavaParser(BaseParser):
    """
    Java code parser using tree-sitter with regex fallback.
    Extracts methods, classes, imports, and complexity metrics from Java code.
    """
    
    def __init__(self):
        """Initialize the Java parser."""
        super().__init__("java")
        self.use_fallback = False
        # Test the parser setup
        if not self.test_simple_parsing():
            logger.warning("Java parser setup validation failed - using regex fallback")
            self.use_fallback = True
    
    def _setup_language(self):
        """Setup tree-sitter Java language."""
        try:
            # Try to load the Java language
            self.language = Language('build/my-languages.so', 'java')
            self.parser.set_language(self.language)
            logger.info("Java language loaded successfully from existing library")
        except Exception as e:
            logger.warning(f"Failed to load existing Java language library: {e}")
            # If not found, try to build it
            try:
                logger.info("Building tree-sitter Java language...")
                Language.build_library(
                    'build/my-languages.so',
                    [
                        'vendor/tree-sitter-java'
                    ]
                )
                self.language = Language('build/my-languages.so', 'java')
                self.parser.set_language(self.language)
                logger.info("Java language built and loaded successfully")
            except Exception as build_error:
                logger.error(f"Failed to build Java language library: {build_error}")
                logger.info("Will use regex fallback for Java parsing")
                self.use_fallback = True
                return
        
        # Test the language setup with a simple query
        try:
            test_query = self.language.query("(identifier) @test")
            logger.debug("Java language query test passed")
        except Exception as query_error:
            logger.error(f"Java language query test failed: {query_error}")
            logger.info("Will use regex fallback for Java parsing")
            self.use_fallback = True
        
        logger.info("Java language setup completed successfully")

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

        # If tree-sitter failed during setup, use regex fallback
        if self.use_fallback:
            return self.parse_file_with_regex(file_path)

        try:
            # Try different encoding methods
            source_code = None
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text_content = f.read()
                    source_code = text_content.encode('utf-8')
                    logger.debug(f"Successfully read {file_path} with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    logger.debug(f"Failed to read {file_path} with {encoding} encoding")
                    continue
            
            if source_code is None:
                # Fallback to binary read
                with open(file_path, 'rb') as f:
                    source_code = f.read()
                logger.debug(f"Using binary read for {file_path}")
            
            # Try to parse the file
            tree = self.parser.parse(source_code)
            
            # Check if parsing was successful
            if tree is None or tree.root_node is None:
                logger.warning(f"Tree-sitter failed for {file_path}, falling back to regex parsing")
                return self.parse_file_with_regex(file_path)
            
            # Check if the tree has errors
            if tree.root_node.has_error:
                logger.warning(f"Java file {file_path} has syntax errors, falling back to regex parsing")
                return self.parse_file_with_regex(file_path)
            
            result = {
                'file_path': file_path,
                'language': 'java',
                'functions': self.extract_methods(tree),
                'classes': self.extract_classes(tree),
                'imports': self.extract_imports(tree),
                'metrics': self.calculate_file_metrics(tree, source_code),
                'has_errors': False,
                'parser_used': 'tree-sitter'
            }
            
            logger.debug(f"Successfully parsed Java file with tree-sitter: {file_path}")
            return result
            
        except Exception as e:
            logger.warning(f"Tree-sitter error parsing Java file {file_path}: {str(e)}, falling back to regex")
            return self.parse_file_with_regex(file_path)

    def parse_file_with_regex(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a Java file using regex patterns as fallback.
        
        Args:
            file_path: Path to the Java file to parse
            
        Returns:
            Dictionary containing parsed Java code features
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            result = {
                'file_path': file_path,
                'language': 'java',
                'functions': self.extract_methods_regex(content),
                'classes': self.extract_classes_regex(content),
                'imports': self.extract_imports_regex(content),
                'metrics': self.calculate_file_metrics_regex(content),
                'has_errors': False,
                'parser_used': 'regex'
            }
            
            logger.debug(f"Successfully parsed Java file with regex: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing Java file with regex {file_path}: {str(e)}")
            return {
                'file_path': file_path,
                'language': 'java',
                'functions': [],
                'classes': [],
                'imports': [],
                'metrics': {'total_lines': 0, 'code_lines': 0, 'comment_lines': 0, 'blank_lines': 0, 'average_complexity': 0},
                'has_errors': True,
                'parser_used': 'regex',
                'error': str(e)
            }

    def extract_methods_regex(self, content: str) -> List[Dict[str, Any]]:
        """Extract method definitions using regex patterns."""
        methods = []
        
        # Pattern to match Java method declarations
        method_pattern = r'(?:public|private|protected|static|\s)*\s+(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            matches = re.finditer(method_pattern, line)
            for match in matches:
                method_name = match.group(1)
                # Skip constructors and common non-method patterns
                if method_name and not method_name in ['if', 'while', 'for', 'switch', 'catch']:
                    methods.append({
                        'name': method_name,
                        'position': {'start_line': i, 'start_column': match.start(), 'end_line': i, 'end_column': match.end()},
                        'parameters': [],  # Empty list of strings
                        'complexity': 1,
                        'body_text': ''
                    })
        
        return methods

    def extract_classes_regex(self, content: str) -> List[Dict[str, Any]]:
        """Extract class definitions using regex patterns."""
        classes = []
        
        # Pattern to match Java class declarations
        class_pattern = r'(?:public|private|protected|abstract|final|\s)*\s*class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[^{]+)?\s*\{'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            matches = re.finditer(class_pattern, line)
            for match in matches:
                class_name = match.group(1)
                classes.append({
                    'name': class_name,
                    'position': {'start_line': i, 'start_column': match.start(), 'end_line': i, 'end_column': match.end()},
                    'methods': [],
                    'complexity': 1,
                    'body_text': ''
                })
        
        return classes

    def extract_imports_regex(self, content: str) -> List[Dict[str, Any]]:
        """Extract import statements using regex patterns."""
        imports = []
        
        # Pattern to match Java import statements
        import_pattern = r'import\s+(?:static\s+)?([^;]+);'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            matches = re.finditer(import_pattern, line)
            for match in matches:
                import_name = match.group(1).strip()
                import_type = "static" if "static" in line else "regular"
                imports.append({
                    'text': line.strip(),
                    'position': {'start_line': i, 'start_column': match.start(), 'end_line': i, 'end_column': match.end()},
                    'type': import_type
                })
        
        return imports

    def calculate_file_metrics_regex(self, content: str) -> Dict[str, Any]:
        """Calculate file metrics using simple text analysis."""
        lines = content.split('\n')
        
        total_lines = len(lines)
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        in_multiline_comment = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('//'):
                comment_lines += 1
            elif stripped.startswith('/*'):
                comment_lines += 1
                in_multiline_comment = True
            elif in_multiline_comment:
                comment_lines += 1
                if '*/' in stripped:
                    in_multiline_comment = False
            else:
                code_lines += 1
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines,
            'average_complexity': 1.0
        }

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
        
        captures = query.captures(tree.root_node)
        
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
                    'parameters': [f"{param['name']}: {param['type']}" for param in self.extract_java_parameters(params_node, source_code)] if params_node else [],
                    'complexity': self.calculate_complexity(capture[0].parent) if capture[0].parent else 1,
                    'body_text': self.get_node_text(body_node, source_code) if body_node else ""
                }
                
                methods.append(method_data)
        
        return methods
    
    def extract_functions(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract function definitions from Java AST.
        
        In Java, functions are methods, so this delegates to extract_methods.
        """
        return self.extract_methods(tree)
    
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
        """Extract import statements from Java AST."""
        imports = []
        source_code = tree.text
        
        # Query for import statements
        query = self.language.query("""
            (import_declaration
                name: (scoped_identifier) @import.name
            )
        """)
        
        captures = query.captures(tree.root_node)
        
        for capture in captures:
            import_name = self.get_node_text(capture[0], source_code)
            # Get the full import line text
            import_text = f"import {import_name};"
            
            import_data = {
                'text': import_text,
                'position': self.get_node_position(capture[0]),
                'type': 'regular'
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
                        'parameters': [f"{param['name']}: {param['type']}" for param in method_params] if method_params else [],
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
        return ['*.java']

    def test_simple_parsing(self):
        """Test parsing with a simple Java snippet to validate the parser setup."""
        simple_java = b"""
public class TestClass {
    public void testMethod() {
        System.out.println("Hello World");
    }
}
"""
        try:
            tree = self.parser.parse(simple_java)
            if tree and tree.root_node and not tree.root_node.has_error:
                logger.info("Simple Java parsing test passed")
                return True
            else:
                logger.error("Simple Java parsing test failed - syntax errors detected")
                return False
        except Exception as e:
            logger.error(f"Simple Java parsing test failed with exception: {e}")
            return False
