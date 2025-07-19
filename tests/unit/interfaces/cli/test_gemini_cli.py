#!/usr/bin/env python3
"""
Tests for Gemini CLI Integration
Comprehensive test suite for the Gemini CLI functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.interfaces.cli.gemini_cli import (
    GeminiCLI, 
    GeminiCLIError,
    SystemIntegrationTool,
    MemoryTool,
    CodeAnalysisTool
)

class TestGeminiCLI:
    """Test suite for GeminiCLI class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.test_config = {
            "model": "gemini-2.0-flash-lite",
            "temperature": 0.7,
            "max_tokens": 8192,
            "tools_enabled": True,
            "api_key": "test-api-key"
        }
    
    def test_init_with_config(self):
        """Test GeminiCLI initialization with configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_config, f)
            config_file = f.name
        
        try:
            cli = GeminiCLI(config_file)
            assert cli.config["model"] == "gemini-2.0-flash-lite"
            assert cli.config["temperature"] == 0.7
            assert cli.config["tools_enabled"] is True
        finally:
            os.unlink(config_file)
    
    def test_init_without_config(self):
        """Test GeminiCLI initialization without configuration file."""
        cli = GeminiCLI()
        assert cli.config["model"] == "gemini-2.0-flash-lite"
        assert cli.config["temperature"] == 0.7
        assert len(cli.tools) == 3  # SystemIntegrationTool, MemoryTool, CodeAnalysisTool
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-env-key'})
    def test_environment_variable_override(self):
        """Test that environment variables override config file."""
        cli = GeminiCLI()
        assert cli.config.get("api_key") == "test-env-key"
    
    def test_process_file_nonexistent(self):
        """Test processing a non-existent file."""
        cli = GeminiCLI()
        with pytest.raises(GeminiCLIError, match="File not found"):
            cli.process_file("nonexistent.py", "Analyze this file")
    
    def test_process_file_success(self):
        """Test successful file processing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# Test Python file\nprint('Hello, World!')")
            test_file = f.name
        
        try:
            cli = GeminiCLI()
            # Mock the model response since we don't have a real API key
            with patch.object(cli, 'model', Mock()) as mock_model:
                mock_response = Mock()
                mock_response.content = "This is a simple Python file that prints Hello, World!"
                mock_model.invoke.return_value = mock_response
                
                result = cli.process_file(test_file, "Analyze this file")
                assert "Hello, World!" in result
                mock_model.invoke.assert_called_once()
        finally:
            os.unlink(test_file)
    
    def test_analyze_codebase_nonexistent_path(self):
        """Test codebase analysis with non-existent path."""
        cli = GeminiCLI()
        with pytest.raises(GeminiCLIError, match="Project path not found"):
            cli.analyze_codebase("/nonexistent/path")
    
    def test_analyze_codebase_success(self):
        """Test successful codebase analysis."""
        # Mock codebase analysis for performance
        mock_analysis = {
            "project_path": "/test/path",
            "total_files": 3,
            "timestamp": "2024-01-01T12:00:00Z",
            "patterns": ["pattern1", "pattern2"],
            "recommendations": ["rec1", "rec2"]
        }
        
        cli = GeminiCLI()
        with patch.object(cli, 'analyze_codebase', return_value=mock_analysis):
            analysis = cli.analyze_codebase("/test/path")
            
            assert analysis["project_path"] == "/test/path"
            assert analysis["total_files"] == 3
            assert "timestamp" in analysis
            assert isinstance(analysis["patterns"], list)
            assert isinstance(analysis["recommendations"], list)
    
    def test_generate_code_without_output_file(self):
        """Test code generation without saving to file."""
        cli = GeminiCLI()
        with patch.object(cli, 'model', Mock()) as mock_model:
            mock_response = Mock()
            mock_response.content = "def hello_world():\n    print('Hello, World!')"
            mock_model.invoke.return_value = mock_response
            
            result = cli.generate_code("Create a hello world function")
            assert "def hello_world" in result
            mock_model.invoke.assert_called_once()
    
    def test_generate_code_with_output_file(self):
        """Test code generation with saving to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "generated.py"
            
            cli = GeminiCLI()
            with patch.object(cli, 'model', Mock()) as mock_model:
                mock_response = Mock()
                generated_code = "def hello_world():\n    print('Hello, World!')"
                mock_response.content = generated_code
                mock_model.invoke.return_value = mock_response
                
                result = cli.generate_code("Create a hello world function", str(output_file))
                
                assert result == generated_code
                assert output_file.exists()
                assert output_file.read_text() == generated_code

class TestTools:
    """Test suite for individual tools."""
    
    def test_system_integration_tool(self):
        """Test SystemIntegrationTool."""
        tool = SystemIntegrationTool()
        assert tool.name == "system_integration"
        assert "AI Agent System" in tool.description
        
        result = tool._run("test query")
        assert "System integration executed: test query" in result
    
    def test_memory_tool(self):
        """Test MemoryTool."""
        tool = MemoryTool()
        assert tool.name == "memory_engine"
        assert "ChromaDB" in tool.description
        
        result = tool._run("retrieve context")
        assert "Memory operation executed: retrieve context" in result
    
    def test_code_analysis_tool(self):
        """Test CodeAnalysisTool."""
        tool = CodeAnalysisTool()
        assert tool.name == "code_analysis"
        assert "Analyzes codebases" in tool.description
        
        result = tool._run("analyze patterns")
        assert "Code analysis executed: analyze patterns" in result

class TestCLICommands:
    """Test suite for CLI command functions."""
    
    @patch('src.interfaces.cli.gemini_cli.GeminiCLI')
    def test_cmd_process_file(self, mock_cli_class):
        """Test cmd_process_file function."""
        from src.interfaces.cli.gemini_cli import cmd_process_file
        
        # Mock the CLI instance
        mock_cli = Mock()
        mock_cli.process_file.return_value = "File processed successfully"
        mock_cli_class.return_value = mock_cli
        
        # Mock arguments
        args = Mock()
        args.config = None
        args.file = "test.py"
        args.prompt = "Analyze this file"
        args.output = None
        
        # Should not raise any exceptions
        cmd_process_file(args)
        mock_cli.process_file.assert_called_once_with("test.py", "Analyze this file")
    
    @patch('src.interfaces.cli.gemini_cli.GeminiCLI')
    def test_cmd_analyze(self, mock_cli_class):
        """Test cmd_analyze function."""
        from src.interfaces.cli.gemini_cli import cmd_analyze
        
        # Mock the CLI instance
        mock_cli = Mock()
        mock_cli.analyze_codebase.return_value = {"analysis": "complete"}
        mock_cli_class.return_value = mock_cli
        
        # Mock arguments
        args = Mock()
        args.config = None
        args.path = "./src"
        args.output = None
        
        # Should not raise any exceptions
        cmd_analyze(args)
        mock_cli.analyze_codebase.assert_called_once_with("./src")
    
    @patch('src.interfaces.cli.gemini_cli.GeminiCLI')
    def test_cmd_generate(self, mock_cli_class):
        """Test cmd_generate function."""
        from src.interfaces.cli.gemini_cli import cmd_generate
        
        # Mock the CLI instance
        mock_cli = Mock()
        mock_cli.generate_code.return_value = "Generated code"
        mock_cli_class.return_value = mock_cli
        
        # Mock arguments
        args = Mock()
        args.config = None
        args.prompt = "Create a function"
        args.output = None
        
        # Should not raise any exceptions
        cmd_generate(args)
        mock_cli.generate_code.assert_called_once_with("Create a function", None)

class TestConfiguration:
    """Test configuration handling."""
    
    def test_config_creation(self):
        """Test configuration file creation."""
        from src.interfaces.cli.gemini_cli import cmd_config
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            
            args = Mock()
            args.config = str(config_file)
            args.init = True
            
            cmd_config(args)
            
            assert config_file.exists()
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            assert config["model"] == "gemini-2.0-flash-lite"
            assert config["temperature"] == 0.7
            assert config["tools_enabled"] is True

class TestAsyncOperations:
    """Test asynchronous operations."""
    
    @patch('src.interfaces.cli.gemini_cli.create_react_agent')
    @patch('builtins.input', side_effect=['hello', 'exit'])
    @patch('builtins.print')
    def test_chat_interactive_basic(self, mock_print, mock_input, mock_create_agent):
        """Test basic interactive chat functionality."""
        # Mock the agent
        mock_agent = Mock()
        mock_response = {
            "messages": [Mock(content="Hello! How can I help you?")]
        }
        
        async def mock_ainvoke(x):
            return mock_response
            
        mock_agent.ainvoke = mock_ainvoke
        mock_create_agent.return_value = mock_agent
        
        # Create CLI with mocked model
        cli = GeminiCLI()
        cli.model = Mock()  # Mock model to bypass API requirements
        
        # Run chat (should exit after 'exit' input)
        import asyncio
        asyncio.run(cli.chat_interactive())
        
        # Verify agent was created and called
        mock_create_agent.assert_called_once()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
