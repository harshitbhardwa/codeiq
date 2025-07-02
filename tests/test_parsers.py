import pytest
import tempfile
import os
from pathlib import Path

from src.parsers.parser_factory import ParserFactory
from src.parsers.python_parser import PythonParser
from src.parsers.go_parser import GoParser
from src.parsers.java_parser import JavaParser

class TestParserFactory:
    """Test cases for ParserFactory."""
    
    def test_get_supported_languages(self):
        """Test getting supported languages."""
        factory = ParserFactory()
        languages = factory.get_supported_languages()
        
        assert 'python' in languages
        assert 'go' in languages
        assert 'java' in languages
        assert 'py' in languages
    
    def test_get_parser(self):
        """Test getting parser for supported language."""
        factory = ParserFactory()
        
        python_parser = factory.get_parser('python')
        assert isinstance(python_parser, PythonParser)
        
        go_parser = factory.get_parser('go')
        assert isinstance(go_parser, GoParser)
        
        java_parser = factory.get_parser('java')
        assert isinstance(java_parser, JavaParser)
    
    def test_get_parser_unsupported_language(self):
        """Test getting parser for unsupported language."""
        factory = ParserFactory()
        
        parser = factory.get_parser('unsupported')
        assert parser is None
    
    def test_get_parser_by_file_extension(self):
        """Test getting parser by file extension."""
        factory = ParserFactory()
        
        # Test Python file
        parser = factory.get_parser_by_file_extension('/path/to/file.py')
        assert isinstance(parser, PythonParser)
        
        # Test Go file
        parser = factory.get_parser_by_file_extension('/path/to/file.go')
        assert isinstance(parser, GoParser)
        
        # Test Java file
        parser = factory.get_parser_by_file_extension('/path/to/file.java')
        assert isinstance(parser, JavaParser)
    
    def test_parser_caching(self):
        """Test that parsers are cached."""
        factory = ParserFactory()
        
        # Get parser twice
        parser1 = factory.get_parser('python')
        parser2 = factory.get_parser('python')
        
        # Should be the same instance
        assert parser1 is parser2
    
    def test_clear_cache(self):
        """Test clearing parser cache."""
        factory = ParserFactory()
        
        # Get parser
        parser1 = factory.get_parser('python')
        
        # Clear cache
        factory.clear_cache()
        
        # Get parser again
        parser2 = factory.get_parser('python')
        
        # Should be different instances
        assert parser1 is not parser2

class TestPythonParser:
    """Test cases for PythonParser."""
    
    def setup_method(self):
        """Setup test method."""
        self.parser = PythonParser()
    
    def test_validate_file(self):
        """Test file validation."""
        # Test with non-existent file
        assert not self.parser.validate_file('/path/to/nonexistent/file.py')
        
        # Test with directory
        with tempfile.TemporaryDirectory() as temp_dir:
            assert not self.parser.validate_file(temp_dir)
    
    def test_get_default_file_patterns(self):
        """Test getting default file patterns."""
        patterns = self.parser._get_default_file_patterns()
        assert patterns == ['*.py']
    
    def test_calculate_complexity(self):
        """Test complexity calculation."""
        # This would need a mock tree-sitter node
        # For now, just test the method exists
        assert hasattr(self.parser, 'calculate_complexity')
    
    def test_get_node_position(self):
        """Test getting node position."""
        # This would need a mock tree-sitter node
        # For now, just test the method exists
        assert hasattr(self.parser, 'get_node_position')

class TestGoParser:
    """Test cases for GoParser."""
    
    def setup_method(self):
        """Setup test method."""
        self.parser = GoParser()
    
    def test_get_default_file_patterns(self):
        """Test getting default file patterns."""
        patterns = self.parser._get_default_file_patterns()
        assert patterns == ['*.go']
    
    def test_validate_file(self):
        """Test file validation."""
        # Test with non-existent file
        assert not self.parser.validate_file('/path/to/nonexistent/file.go')

class TestJavaParser:
    """Test cases for JavaParser."""
    
    def setup_method(self):
        """Setup test method."""
        self.parser = JavaParser()
    
    def test_get_default_file_patterns(self):
        """Test getting default file patterns."""
        patterns = self.parser._get_default_file_patterns()
        assert patterns == ['*.java']
    
    def test_validate_file(self):
        """Test file validation."""
        # Test with non-existent file
        assert not self.parser.validate_file('/path/to/nonexistent/file.java')

# Integration tests
class TestParserIntegration:
    """Integration tests for parsers."""
    
    def test_python_file_parsing(self):
        """Test parsing a simple Python file."""
        parser = PythonParser()
        
        # Create a simple Python file
        python_code = '''
def hello_world():
    """Simple hello world function."""
    print("Hello, World!")

class Calculator:
    def add(self, a, b):
        return a + b
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_file = f.name
        
        try:
            result = parser.parse_file(temp_file)
            
            # Check basic structure
            assert result is not None
            assert 'file_path' in result
            assert 'language' in result
            assert result['language'] == 'python'
            
            # Check functions
            assert 'functions' in result
            functions = result['functions']
            assert len(functions) >= 1
            
            # Check classes
            assert 'classes' in result
            classes = result['classes']
            assert len(classes) >= 1
            
            # Check imports
            assert 'imports' in result
            
            # Check metrics
            assert 'metrics' in result
            metrics = result['metrics']
            assert 'total_lines' in metrics
            assert 'code_lines' in metrics
            
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_go_file_parsing(self):
        """Test parsing a simple Go file."""
        parser = GoParser()
        
        # Create a simple Go file
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as f:
            f.write(go_code)
            temp_file = f.name
        
        try:
            result = parser.parse_file(temp_file)
            
            # Check basic structure
            assert result is not None
            assert 'file_path' in result
            assert 'language' in result
            assert result['language'] == 'go'
            
            # Check functions
            assert 'functions' in result
            
            # Check structs
            assert 'structs' in result
            
            # Check imports
            assert 'imports' in result
            
            # Check metrics
            assert 'metrics' in result
            
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_java_file_parsing(self):
        """Test parsing a simple Java file."""
        parser = JavaParser()
        
        # Create a simple Java file
        java_code = '''
import java.util.List;

public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
    
    public int add(int a, int b) {
        return a + b;
    }
}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(java_code)
            temp_file = f.name
        
        try:
            result = parser.parse_file(temp_file)
            
            # Check basic structure
            assert result is not None
            assert 'file_path' in result
            assert 'language' in result
            assert result['language'] == 'java'
            
            # Check methods
            assert 'methods' in result
            
            # Check classes
            assert 'classes' in result
            
            # Check imports
            assert 'imports' in result
            
            # Check metrics
            assert 'metrics' in result
            
        finally:
            # Clean up
            os.unlink(temp_file) 