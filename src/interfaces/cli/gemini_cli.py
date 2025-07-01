#!/usr/bin/env python3
"""
Gemini CLI Integration for AI Agent System
Provides command-line interface for Google Gemini AI integration with LangChain, LangGraph, and MCP support.
Based on Google's official Gemini CLI (June 2025) with custom integrations for the AI Agent System.
"""

import sys
import os
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import real LangChain and Gemini packages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

class GeminiCLIError(Exception):
    """Custom exception for Gemini CLI errors."""
    pass

class SystemIntegrationTool(BaseTool):
    """Tool for integrating with the AI Agent System."""
    
    name: str = "system_integration"
    description: str = "Integrates with the AI Agent System for task execution and memory operations."
    
    def _run(self, query: str) -> str:
        """Execute system integration operations."""
        try:
            # This would integrate with your existing agent system
            return f"System integration executed: {query}"
        except Exception as e:
            return f"Error in system integration: {str(e)}"

class MemoryTool(BaseTool):
    """Tool for memory engine operations."""
    
    name: str = "memory_engine"
    description: str = "Interacts with the ChromaDB-based memory engine for context retrieval and storage."
    
    def _run(self, query: str) -> str:
        """Execute memory operations."""
        try:
            # This would integrate with your memory engine
            return f"Memory operation executed: {query}"
        except Exception as e:
            return f"Error in memory operation: {str(e)}"

class CodeAnalysisTool(BaseTool):
    """Tool for code analysis and generation."""
    
    name: str = "code_analysis"
    description: str = "Analyzes codebases and generates code following the project's architecture patterns."
    
    def _run(self, query: str) -> str:
        """Execute code analysis operations."""
        try:
            # This would integrate with your code analysis tools
            return f"Code analysis executed: {query}"
        except Exception as e:
            return f"Error in code analysis: {str(e)}"

class GeminiCLI:
    """Main Gemini CLI interface for AI Agent System integration."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize Gemini CLI with configuration."""
        self.config = self._load_config(config_file)
        self.model: Optional[ChatGoogleGenerativeAI] = None
        self.tools: List[BaseTool] = []
        self._setup_model()
        self._setup_tools()
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or environment."""
        default_config = {
            "model": "gemini-2.0-flash-lite",
            "temperature": 0.7,
            "max_tokens": 8192,
            "system_instruction": "You are an AI assistant integrated with a sophisticated multi-agent system. You have access to memory engines, code analysis tools, and system integration capabilities.",
            "tools_enabled": True,
            "mcp_integration": True,
            "langgraph_integration": True
        }
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")
        
        # Override with environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            default_config["api_key"] = api_key
        
        return default_config
    
    def _setup_model(self):
        """Setup the Gemini model."""
        try:
            self.model = ChatGoogleGenerativeAI(
                model=self.config.get("model", "gemini-2.0-flash-lite"),
                temperature=self.config.get("temperature", 0.7),
                google_api_key=self.config.get("api_key", os.getenv("GEMINI_API_KEY"))
            )
            logger.info(f"Gemini model initialized: {self.config.get('model')}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            self.model = None
    
    def _setup_tools(self):
        """Setup available tools for the agent."""
        if not self.config.get("tools_enabled", True):
            return
        
        self.tools = [
            SystemIntegrationTool(),
            MemoryTool(),
            CodeAnalysisTool()
        ]
        logger.info(f"Initialized {len(self.tools)} tools")
    
    async def chat_interactive(self):
        """Start interactive chat session."""
        print("🚀 Gemini CLI - AI Agent System Integration")
        print("=" * 60)
        print("Type 'exit' to quit, 'help' for commands")
        print()
        
        if not self.model:
            print("❌ Gemini model not available. Check your API key and configuration.")
            return
        
        try:
            # Create ReAct agent with tools
            agent = create_react_agent(self.model, self.tools)
            
            while True:
                try:
                    user_input = input("💬 You: ").strip()
                    
                    if user_input.lower() in ['exit', 'quit']:
                        print("👋 Goodbye!")
                        break
                    
                    if user_input.lower() == 'help':
                        self._show_help()
                        continue
                    
                    if not user_input:
                        continue
                    
                    # Process with agent
                    print("🤖 Gemini: ", end="")
                    response = await agent.ainvoke({"messages": [HumanMessage(content=user_input)]})
                    print(response["messages"][-1].content)
                    print()
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Chat session error: {e}")
            print(f"❌ Failed to start chat session: {e}")
    
    def process_file(self, file_path: str, prompt: str) -> str:
        """Process a file with Gemini."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise GeminiCLIError(f"File not found: {file_path_obj}")
            
            # Read file content
            content = file_path_obj.read_text(encoding='utf-8')
            
            # Create combined prompt
            full_prompt = f"""
File: {file_path_obj}
Content:
```
{content}
```

Task: {prompt}
"""
            
            if self.model:
                response = self.model.invoke([HumanMessage(content=full_prompt)])
                # Handle different content types from Gemini response
                if isinstance(response.content, str):
                    return response.content
                elif isinstance(response.content, list):
                    # Join list items into a string
                    return "\n".join(str(item) for item in response.content)
                else:
                    return str(response.content)
            else:
                raise GeminiCLIError("Gemini model not initialized. Check your API key and configuration.")
                
        except Exception as e:
            raise GeminiCLIError(f"File processing error: {e}")
    
    def analyze_codebase(self, project_path: str) -> Dict[str, Any]:
        """Analyze entire codebase structure and patterns."""
        try:
            project_path_obj = Path(project_path)
            if not project_path_obj.exists():
                raise GeminiCLIError(f"Project path not found: {project_path_obj}")
            
            # Collect Python files
            python_files = list(project_path_obj.rglob("*.py"))
            
            analysis = {
                "project_path": str(project_path_obj),
                "total_files": len(python_files),
                "timestamp": datetime.now().isoformat(),
                "patterns": [],
                "recommendations": []
            }
            
            # Analyze patterns (simplified for demo)
            if len(python_files) > 0:
                analysis["patterns"].append("Multi-module Python project")
                analysis["recommendations"].append("Consider implementing comprehensive testing")
            
            return analysis
            
        except Exception as e:
            raise GeminiCLIError(f"Codebase analysis error: {e}")
    
    def generate_code(self, prompt: str, output_file: Optional[str] = None) -> str:
        """Generate code based on prompt."""
        try:
            if self.model:
                system_prompt = f"""
You are a code generation expert working with a sophisticated AI agent system.
Generate high-quality, production-ready code following these principles:
- Clean Architecture and Domain-Driven Design
- Comprehensive type hints and documentation
- Error handling and validation
- Testing considerations
- Following the project's existing patterns

Task: {prompt}
"""
                response = self.model.invoke([HumanMessage(content=system_prompt)])
                # Handle different content types from Gemini response
                if isinstance(response.content, str):
                    generated_code = response.content
                elif isinstance(response.content, list):
                    generated_code = "\n".join(str(item) for item in response.content)
                else:
                    generated_code = str(response.content)
            else:
                raise GeminiCLIError("Gemini model not initialized. Check your API key and configuration.")
            
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(generated_code, encoding='utf-8')
                logger.info(f"Code saved to: {output_path}")
            
            return generated_code
            
        except Exception as e:
            raise GeminiCLIError(f"Code generation error: {e}")
    
    def _show_help(self):
        """Show help information."""
        help_text = """
🎯 Gemini CLI Commands:

Interactive Commands:
  help          - Show this help
  exit/quit     - Exit the chat

Available Tools:
  • system_integration - Integrate with AI Agent System
  • memory_engine      - Access ChromaDB memory operations  
  • code_analysis      - Analyze and generate code

Example Prompts:
  "Analyze the memory engine architecture"
  "Generate a new agent following the system patterns"
  "Review the test coverage for the HITL module"
  "Suggest improvements for the LangGraph workflows"

Configuration:
  Set GEMINI_API_KEY environment variable
  Use --config to specify custom configuration file
"""
        print(help_text)

async def cmd_chat(args):
    """Start interactive chat session."""
    cli = GeminiCLI(args.config)
    await cli.chat_interactive()

def cmd_process_file(args):
    """Process a single file."""
    cli = GeminiCLI(args.config)
    try:
        result = cli.process_file(args.file, args.prompt)
        print("🎯 Result:")
        print(result)
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result, encoding='utf-8')
            print(f"📁 Output saved to: {output_path}")
            
    except GeminiCLIError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def cmd_analyze(args):
    """Analyze codebase."""
    cli = GeminiCLI(args.config)
    try:
        analysis = cli.analyze_codebase(args.path)
        print("📊 Codebase Analysis:")
        print(json.dumps(analysis, indent=2))
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(analysis, f, indent=2)
            print(f"📁 Analysis saved to: {output_path}")
            
    except GeminiCLIError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def cmd_generate(args):
    """Generate code."""
    cli = GeminiCLI(args.config)
    try:
        code = cli.generate_code(args.prompt, args.output)
        if not args.output:
            print("🎯 Generated Code:")
            print(code)
    except GeminiCLIError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def cmd_config(args):
    """Show or create configuration."""
    config_path = Path(args.config) if args.config else Path("gemini.json")
    
    if args.init:
        # Create default configuration
        default_config = {
            "model": "gemini-2.0-flash-lite",
            "temperature": 0.7,
            "max_tokens": 8192,
            "system_instruction": "You are an AI assistant integrated with a sophisticated multi-agent system.",
            "tools_enabled": True,
            "mcp_integration": True,
            "langgraph_integration": True
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"✅ Configuration file created: {config_path}")
    else:
        # Show current configuration
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"📋 Configuration from {config_path}:")
            print(json.dumps(config, indent=2))
        else:
            print(f"❌ Configuration file not found: {config_path}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Gemini CLI for AI Agent System Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive chat
  python gemini_cli.py chat
  
  # Process a file
  python gemini_cli.py process README.md "Summarize this documentation"
  
  # Analyze codebase
  python gemini_cli.py analyze ./src --output analysis.json
  
  # Generate code
  python gemini_cli.py generate "Create a new HITL checkpoint validator" --output validator.py
  
  # Setup configuration
  python gemini_cli.py config --init
        """
    )
    
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start interactive chat session")
    chat_parser.set_defaults(func=cmd_chat)
    
    # Process file command
    process_parser = subparsers.add_parser("process", help="Process a file with Gemini")
    process_parser.add_argument("file", help="File to process")
    process_parser.add_argument("prompt", help="Processing prompt")
    process_parser.add_argument("--output", "-o", help="Output file")
    process_parser.set_defaults(func=cmd_process_file)
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze codebase")
    analyze_parser.add_argument("path", help="Project path to analyze")
    analyze_parser.add_argument("--output", "-o", help="Output file for analysis")
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate code")
    generate_parser.add_argument("prompt", help="Code generation prompt")
    generate_parser.add_argument("--output", "-o", help="Output file")
    generate_parser.set_defaults(func=cmd_generate)
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_parser.add_argument("--init", action="store_true", help="Initialize default configuration")
    config_parser.set_defaults(func=cmd_config)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Setup logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check for API key
    if args.command != "config" and not os.getenv("GEMINI_API_KEY"):
        print("⚠️  GEMINI_API_KEY environment variable not set.")
        print("   Get your API key from: https://ai.google.dev/")
        print("   Set it with: export GEMINI_API_KEY='your-key-here'")
        print()
    
    # Execute command
    try:
        if asyncio.iscoroutinefunction(args.func):
            asyncio.run(args.func(args))
        else:
            args.func(args)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
