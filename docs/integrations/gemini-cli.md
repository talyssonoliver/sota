# Gemini CLI Integration

## Overview

The Gemini CLI Integration provides a command-line interface for Google Gemini AI that's specifically designed to work with our sophisticated AI Agent System. This integration combines Google's official Gemini CLI capabilities with our existing LangChain, LangGraph, and Model Context Protocol (MCP) infrastructure.

## Features

### 🚀 Core Capabilities
- **Interactive Chat Session** with context-aware responses
- **File Processing** with project-specific understanding
- **Codebase Analysis** following our architecture patterns
- **Code Generation** adhering to Clean Architecture and DDD principles
- **Memory Engine Integration** with ChromaDB-based context retrieval
- **System Integration** with existing agents and workflows

### 🛠️ Technical Integration
- **LangChain Integration**: Uses `langchain-google-genai` for seamless model access
- **LangGraph Support**: Creates ReAct agents with tool integration
- **MCP Compatibility**: Follows Model Context Protocol standards
- **Tool Ecosystem**: Integrated with system tools and memory operations

## Installation

### Prerequisites
1. **Node.js 18+** (for official Gemini CLI features)
2. **Python 3.9+** (for system integration)
3. **Google API Key** from [Google AI Studio](https://ai.google.dev/)

### Install Dependencies

```bash
# Install Google Gemini AI integration
pip install langchain-google-genai google-generativeai

# Optional: Install official Gemini CLI globally
npm install -g @google/gemini-cli
```

### Setup API Key

```bash
# Set environment variable
export GEMINI_API_KEY="your-gemini-api-key-here"

# Or add to your .env file
echo "GEMINI_API_KEY=your-gemini-api-key-here" >> .env
```

## Configuration

### Create Configuration File

```bash
# Initialize default configuration
python src/interfaces/cli/gemini_cli.py config --init

# Or use the provided template
cp config/gemini_config.json gemini.json
```

### Configuration Options

```json
{
  "model": "gemini-2.0-flash-lite",
  "temperature": 0.7,
  "max_tokens": 8192,
  "tools_enabled": true,
  "mcp_integration": true,
  "langgraph_integration": true
}
```

## Usage

### Interactive Chat Session

```bash
# Start interactive chat with system integration
python src/interfaces/cli/gemini_cli.py chat

# Use custom configuration
python src/interfaces/cli/gemini_cli.py --config config/gemini_config.json chat
```

Example chat session:
```
🚀 Gemini CLI - AI Agent System Integration
Type 'exit' to quit, 'help' for commands

💬 You: Analyze the HITL workflow architecture
🤖 Gemini: [Analyzes the Human-in-the-Loop system architecture...]

💬 You: Generate a new validation checkpoint for memory operations
🤖 Gemini: [Generates code following project patterns...]
```

### File Processing

```bash
# Process and analyze a specific file
python src/interfaces/cli/gemini_cli.py process src/core/memory/engine.py "Review this code for optimization opportunities"

# Save output to file
python src/interfaces/cli/gemini_cli.py process README.md "Create a technical summary" --output technical_summary.md
```

### Codebase Analysis

```bash
# Analyze entire project structure
python src/interfaces/cli/gemini_cli.py analyze ./src --output analysis.json

# Analyze specific module
python src/interfaces/cli/gemini_cli.py analyze ./src/core/agents --output agents_analysis.json
```

### Code Generation

```bash
# Generate new code following project patterns
python src/interfaces/cli/gemini_cli.py generate "Create a new agent for document processing" --output src/agents/document_agent.py

# Generate test files
python src/interfaces/cli/gemini_cli.py generate "Create comprehensive tests for the memory engine" --output tests/test_memory_engine.py
```

## Available Tools

The Gemini CLI integration provides several specialized tools:

### 1. System Integration Tool
- Connects with existing AI Agent System
- Executes workflows through LangGraph
- Manages agent coordination

### 2. Memory Engine Tool  
- Interacts with ChromaDB vector database
- Performs semantic search and context retrieval
- Manages knowledge storage and indexing

### 3. Code Analysis Tool
- Analyzes code following project architecture
- Suggests improvements based on patterns
- Validates against quality gates

## Integration with Existing Systems

### LangGraph Workflows

```python
# The CLI creates ReAct agents that integrate with existing workflows
agent = create_react_agent(model, tools)
response = await agent.ainvoke({"messages": [HumanMessage(content=prompt)]})
```

### Memory Engine Integration

```python
# Tools automatically connect to the ChromaDB memory system
memory_tool = MemoryTool()
result = memory_tool._run("Retrieve context about agent architectures")
```

### Quality Gates Compliance

The generated code automatically follows project standards:
- **Type Safety**: 100% type hints using Pydantic models
- **Testing**: TDD patterns with pytest
- **Documentation**: Comprehensive docstrings
- **Architecture**: Clean Architecture and DDD principles
- **Security**: Follows OWASP guidelines

## Examples

### Working with Existing Codebase

```bash
# Understand the system architecture
python src/interfaces/cli/gemini_cli.py chat
> "Describe the main pieces of this system's architecture"
> "What security mechanisms are in place?"
> "How does the memory engine integrate with agents?"
```

### Automating Development Tasks

```bash
# Generate implementation for GitHub issues
python src/interfaces/cli/gemini_cli.py generate "Implement first draft for GitHub issue #123" --output implementation.py

# Create migration plans
python src/interfaces/cli/gemini_cli.py generate "Help me migrate this codebase to use the latest LangGraph version. Start with a plan."
```

### System Maintenance

```bash
# Analyze test coverage
python src/interfaces/cli/gemini_cli.py process tests/ "Analyze test coverage and suggest improvements"

# Review security patterns
python src/interfaces/cli/gemini_cli.py analyze src/ "Focus on security patterns and potential vulnerabilities"
```

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```bash
   ⚠️  GEMINI_API_KEY environment variable not set.
   ```
   **Solution**: Set your API key as described in the setup section.

2. **LangChain Import Errors**
   ```bash
   pip install langchain-google-genai google-generativeai
   ```

3. **Configuration Not Found**
   ```bash
   python src/interfaces/cli/gemini_cli.py config --init
   ```

### Debug Mode

```bash
# Enable verbose logging
python src/interfaces/cli/gemini_cli.py --verbose chat
```

## Official Gemini CLI Integration

This custom CLI can work alongside Google's official Gemini CLI:

```bash
# Use official CLI for general tasks
npx @google/gemini-cli
gemini

# Use our custom CLI for system-specific tasks
python src/interfaces/cli/gemini_cli.py chat
```

## Performance Considerations

- **Context Window**: Utilizes Gemini 2.5 Pro's 1M token context window
- **Rate Limits**: 60 requests/minute, 1,000 requests/day with free tier
- **Caching**: Integrates with existing L1/L2 memory caches
- **Async Operations**: Uses asyncio for non-blocking operations

## Security

- **API Key Management**: Secure environment variable storage
- **Input Validation**: All inputs sanitized and validated
- **Output Sanitization**: Prevents injection attacks
- **Audit Trail**: All operations logged for security review

## Contributing

Follow the project's standard contribution guidelines:

1. **Branch Naming**: `feat/gemini-cli/<feature>`
2. **Testing**: 90%+ coverage requirement
3. **Quality Gates**: Pass all linting and security scans
4. **Documentation**: Update this README for new features

## License

This integration follows the project's existing license terms while respecting Google's Gemini CLI Apache 2.0 license.
