import tree_sitter
from tree_sitter import Language, Parser
from typing import Dict, List, Any
from pathlib import Path
from loguru import logger

from .base_parser import BaseParser

class GoParser(BaseParser):
    """
    Go code parser using tree-sitter.
    Extracts functions, structs, imports, and complexity metrics from Go code.
    """
    
    def __init__(self):
        """Initialize the Go parser."""
        super().__init__("go")
    
    def _setup_language(self):
        """Setup tree-sitter Go language."""
        try:
            # Try to load the Go language
            self.language = Language('build/my-languages.so', 'go')
        except Exception:
            # If not found, try to build it
            logger.info("Building tree-sitter Go language...")
            Language.build_library(
                'build/my-languages.so',
                [
                    'vendor/tree-sitter-go'
                ]
            )
            self.language = Language('build/my-languages.so', 'go')
        
        self.parser.set_language(self.language)
        logger.info("Go language setup completed")
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a Go file and extract code features.
        
        Args:
            file_path: Path to the Go file to parse
            
        Returns:
            Dictionary containing parsed Go code features
        """
        if not self.validate_file(file_path):
            return {}
        
        try:
            with open(file_path, 'rb') as f:
                source_code = f.read()
            
            tree = self.parser.parse(source_code)
            
            result = {
                'file_path': file_path,
                'language': 'go',
                'functions': self.extract_functions(tree),
                'structs': self.extract_structs(tree),
                'imports': self.extract_imports(tree),
                'metrics': self.calculate_file_metrics(tree, source_code)
            }
            
            logger.debug(f"Parsed Go file: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing Go file {file_path}: {str(e)}")
            return {}
    
    def extract_functions(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract function definitions from Go AST."""
        functions = []
        source_code = tree.text
        
        # Query for function definitions
        query = self.language.query("""
            (function_declaration
                name: (identifier) @function.name
                parameters: (parameter_list) @function.params
                result: (parameter_list)? @function.result
                body: (block) @function.body
            )
        """)
        
        captures = query.capture(tree.root_node)
        
        for capture in captures:
            if capture[1] == "function.name":
                function_name = self.get_node_text(capture[0], source_code)
                
                # Find corresponding parameters, result, and body
                params_node = None
                result_node = None
                body_node = None
                
                for other_capture in captures:
                    if other_capture[0].parent == capture[0].parent:
                        if other_capture[1] == "function.params":
                            params_node = other_capture[0]
                        elif other_capture[1] == "function.result":
                            result_node = other_capture[0]
                        elif other_capture[1] == "function.body":
                            body_node = other_capture[0]
                
                function_data = {
                    'name': function_name,
                    'position': self.get_node_position(capture[0]),
                    'parameters': self.extract_go_parameters(params_node, source_code) if params_node else [],
                    'return_types': self.extract_go_parameters(result_node, source_code) if result_node else [],
                    'complexity': self.calculate_complexity(capture[0].parent) if capture[0].parent else 1,
                    'body_text': self.get_node_text(body_node, source_code) if body_node else ""
                }
                
                functions.append(function_data)
        
        return functions
    
    def extract_structs(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract struct definitions from Go AST."""
        structs = []
        source_code = tree.text
        
        # Query for struct definitions
        query = self.language.query("""
            (type_declaration
                (type_spec
                    name: (type_identifier) @struct.name
                    type: (struct_type
                        field_declaration_list: (field_declaration_list) @struct.fields
                    )
                )
            )
        """)
        
        captures = query.capture(tree.root_node)
        
        for capture in captures:
            if capture[1] == "struct.name":
                struct_name = self.get_node_text(capture[0], source_code)
                
                # Find corresponding fields
                fields_node = None
                for other_capture in captures:
                    if other_capture[0].parent.parent == capture[0].parent.parent and other_capture[1] == "struct.fields":
                        fields_node = other_capture[0]
                        break
                
                struct_data = {
                    'name': struct_name,
                    'position': self.get_node_position(capture[0]),
                    'fields': self.extract_struct_fields(fields_node, source_code) if fields_node else [],
                    'body_text': self.get_node_text(capture[0].parent, source_code) if capture[0].parent else ""
                }
                
                structs.append(struct_data)
        
        return structs
    
    def extract_imports(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract import statements from Go AST."""
        imports = []
        source_code = tree.text
        
        # Query for import statements
        query = self.language.query("""
            (import_declaration
                (import_spec_list
                    (import_spec
                        path: (interpreted_string_literal) @import.path
                        name: (package_identifier)? @import.name
                    )
                )
            )
        """)
        
        captures = query.capture(tree.root_node)
        
        for capture in captures:
            if capture[1] == "import.path":
                import_path = self.get_node_text(capture[0], source_code).strip('"')
                
                # Find corresponding name if exists
                import_name = None
                for other_capture in captures:
                    if other_capture[0].parent == capture[0].parent and other_capture[1] == "import.name":
                        import_name = self.get_node_text(other_capture[0], source_code)
                        break
                
                import_data = {
                    'path': import_path,
                    'name': import_name,
                    'position': self.get_node_position(capture[0]),
                    'text': f"import {import_name + ' ' if import_name else ''}\"{import_path}\""
                }
                imports.append(import_data)
        
        return imports
    
    def extract_go_parameters(self, params_node: tree_sitter.Node, source_code: bytes) -> List[Dict[str, str]]:
        """Extract parameter information from Go parameter list."""
        if not params_node:
            return []
        
        parameters = []
        
        for child in params_node.children:
            if child.type == 'parameter_declaration':
                param_name = None
                param_type = None
                
                for grandchild in child.children:
                    if grandchild.type == 'identifier':
                        param_name = self.get_node_text(grandchild, source_code)
                    elif grandchild.type in ['type_identifier', 'pointer_type', 'array_type', 'slice_type']:
                        param_type = self.get_node_text(grandchild, source_code)
                
                if param_name:
                    parameters.append({
                        'name': param_name,
                        'type': param_type or 'interface{}'
                    })
        
        return parameters
    
    def extract_struct_fields(self, fields_node: tree_sitter.Node, source_code: bytes) -> List[Dict[str, str]]:
        """Extract field information from Go struct field declaration list."""
        if not fields_node:
            return []
        
        fields = []
        
        for child in fields_node.children:
            if child.type == 'field_declaration_list':
                for grandchild in child.children:
                    if grandchild.type == 'field_declaration':
                        field_name = None
                        field_type = None
                        field_tag = None
                        
                        for great_grandchild in grandchild.children:
                            if great_grandchild.type == 'field_identifier':
                                field_name = self.get_node_text(great_grandchild, source_code)
                            elif great_grandchild.type in ['type_identifier', 'pointer_type', 'array_type', 'slice_type']:
                                field_type = self.get_node_text(great_grandchild, source_code)
                            elif great_grandchild.type == 'raw_string_literal':
                                field_tag = self.get_node_text(great_grandchild, source_code)
                        
                        if field_name:
                            fields.append({
                                'name': field_name,
                                'type': field_type or 'interface{}',
                                'tag': field_tag
                            })
        
        return fields
    
    def calculate_file_metrics(self, tree: tree_sitter.Tree, source_code: bytes) -> Dict[str, Any]:
        """Calculate various metrics for the Go file."""
        lines = source_code.decode('utf-8').split('\n')
        
        metrics = {
            'total_lines': len(lines),
            'code_lines': len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            'comment_lines': len([line for line in lines if line.strip().startswith('//')]),
            'blank_lines': len([line for line in lines if not line.strip()]),
            'average_complexity': 0
        }
        
        # Calculate average complexity
        all_nodes = [tree.root_node]
        total_complexity = 0
        node_count = 0
        
        while all_nodes:
            node = all_nodes.pop(0)
            if node.type in ['function_declaration', 'type_declaration']:
                complexity = self.calculate_complexity(node)
                total_complexity += complexity
                node_count += 1
            
            all_nodes.extend(node.children)
        
        if node_count > 0:
            metrics['average_complexity'] = total_complexity / node_count
        
        return metrics
    
    def _get_default_file_patterns(self) -> List[str]:
        """Get default file patterns for Go files."""
        return ['*.go'] 