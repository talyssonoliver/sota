# Technical Context: AI Agent System Technology Stack

## Core Technologies

### 1. AI & Language Models
- **OpenAI GPT**: Primary language model for agent reasoning
  - Model: `gpt-3.5-turbo-16k` for most operations
  - API Integration: `openai==1.77.0`
  - Token Management: `tiktoken==0.8.0`

### 2. Agent Framework Stack
- **LangChain**: `langchain==0.3.25`
  - Agent orchestration and tool integration
  - Memory management and context handling
  - Chain composition for complex workflows

- **LangGraph**: `langgraph==0.4.1`
  - Workflow orchestration as directed graphs
  - State management with TypedDict schemas
  - Dynamic routing and parallel execution

- **CrewAI**: `crewai==0.118.0`
  - Specialized agent creation and management
  - Role-based agent configuration
  - Multi-agent coordination patterns

### 3. Vector Database & Memory
- **ChromaDB**: Vector database for context storage
  - Semantic search capabilities
  - Embedding-based context retrieval
  - Local persistence with cloud sync options

### 4. External Integrations
- **Supabase**: `supabase==2.15.1`
  - Database operations and schema management
  - Real-time subscriptions
  - Row Level Security (RLS) integration

- **HTTP Clients**: 
  - `httpx==0.28.1` for async operations
  - `requests==2.32.3` for synchronous calls

## Development Environment

### 1. Python Environment
- **Version**: Python 3.9+
- **Package Management**: pip with requirements.txt
- **Virtual Environment**: `.venv` for isolation

### 2. Development Tools
- **Code Formatting**: `black==25.1.0`
- **Import Sorting**: `isort==6.0.1`
- **Environment Management**: `python-dotenv==1.1.0`
- **CLI Framework**: `typer==0.15.3`

### 3. Development Workflow
- **Jupyter Integration**: `jupyterlab==4.4.1` for experimentation
- **File Watching**: `watchdog==6.0.0` for auto-reload
- **Rich Output**: `rich==13.7.0` for enhanced console output

## Testing & Quality Assurance

### 1. Testing Framework
- **Primary**: `pytest==8.3.5`
- **Coverage**: `pytest-cov==6.1.1`
- **Test Structure**: Unified test runner with multiple modes

### 2. Test Categories
```python
# Quick validation tests
python -m tests.run_tests --quick

# Tool integration tests  
python -m tests.run_tests --tools

# Full test suite
python -m tests.run_tests --full
```

### 3. Mock Environment
- **Dependency Mocking**: External API simulation
- **Test Isolation**: No external dependencies required
- **CI/CD Ready**: All tests runnable without API keys

## Data Processing & Storage

### 1. Document Processing
- **HTML Parsing**: `beautifulsoup4==4.13.4`
- **Markdown**: `markdown==3.8`
- **Front Matter**: `python-frontmatter==1.1.0`

### 2. Configuration Management
- **YAML Processing**: `pyyaml==6.0.1`
- **Schema Validation**: JSON Schema for task definitions
- **Environment Variables**: `.env` file management

### 3. Storage Architecture
```
storage/
├── cold/          # Long-term archival
├── warm/          # Recently accessed
└── cache/         # High-frequency access
```

## Security & Performance

### 1. Memory Engine Security
- **Encryption**: Fernet/AES-GCM implementation
- **PII Detection**: Comprehensive pattern matching
- **Hash Security**: SHA256 (replaced insecure hash())
- **Input Sanitization**: XSS and injection protection

### 2. Performance Optimization
- **Multi-tier Caching**: L1 (memory) + L2 (disk) + Cold storage
- **Access Patterns**: LRU eviction with smart preloading
- **Partition Management**: Automatic lifecycle management
- **Health Monitoring**: Performance metrics and alerts

### 3. Logging & Monitoring
- **Structured Logging**: `python-json-logger`
- **Audit Trails**: Complete operation logging
- **Error Tracking**: Comprehensive error classification
- **Performance Metrics**: Response time and throughput monitoring

## Development Setup

### 1. Installation Process
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment configuration
cp .env.template .env
# Edit .env with API keys
```

### 2. Required Environment Variables
```bash
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 3. Development Commands
```bash
# Run main system
python main.py

# Execute specific task
python orchestration/execute_task.py --task BE-07

# Run workflow
python orchestration/execute_workflow.py --all

# Run tests
python -m tests.run_tests --all
```

## Tool Integration Architecture

### 1. Tool Loader Pattern
```python
# tools/tool_loader.py
class ToolLoader:
    def load_tools_for_agent(self, agent_type):
        config = load_tool_config(agent_type)
        return [self.instantiate_tool(tool_def) for tool_def in config]
```

### 2. Available Tools
- **EchoTool**: Basic testing and validation
- **SupabaseTool**: Database operations
- **GitHubTool**: Repository management
- **MemoryEngine**: Context retrieval
- **TestingTools**: Jest, Cypress, Coverage
- **DesignSystemTool**: UI component management
- **TailwindTool**: CSS framework integration
- **VercelTool**: Deployment management

### 3. Tool Configuration
```yaml
# config/tools.yaml
backend_engineer:
  - supabase_tool
  - memory_engine
  - github_tool
  
frontend_engineer:
  - design_system_tool
  - tailwind_tool
  - memory_engine
```

## Deployment & Operations

### 1. System Requirements
- **OS**: Windows 11 (primary), cross-platform compatible
- **Memory**: 8GB+ recommended for vector operations
- **Storage**: SSD recommended for cache performance
- **Network**: Stable internet for API calls

### 2. Performance Targets
- **Context Retrieval**: <1 second response time
- **Agent Response**: <30 seconds for complex tasks
- **Memory Operations**: <100ms for cached data
- **Test Execution**: <5 minutes for full suite

### 3. Monitoring & Maintenance
- **Health Checks**: Automated system validation
- **Cache Management**: Automatic cleanup and optimization
- **Log Rotation**: Structured log management
- **Backup Strategy**: Critical data preservation

## Recent Enhancements (Current Session)

### 1. Enhanced Documentation System
- **README.md**: Comprehensive project overview with architecture details
- **Quick Start Guide**: Streamlined usage instructions with practical examples
- **System Architecture**: Detailed breakdown of all major components
- **Professional Structure**: Organized sections with emojis and clear hierarchy

### 2. Improved Main Interface (main.py)
- **Professional CLI**: Argument parsing with --test and --quiet options
- **Robust Validation**: Enhanced test functions with proper error handling
- **Structured Logging**: File and console output with appropriate levels
- **User Experience**: Clear status indicators (✅/❌/⚠️) and summary reports
- **Comprehensive Testing**: Integration with existing test runner

### 3. Memory Bank Optimization
- **Hierarchical Structure**: Six core files with clear dependencies
- **Current State Alignment**: All documentation reflects production-ready status
- **Context Integration**: Proper integration patterns with existing Memory Engine
- **Maintenance Guidelines**: Clear update triggers and quality standards

### 4. Directory Structure Reorganization
- **Root Directory Cleanup**: Reduced from 40+ to 37 organized items
- **Logical Grouping**: Separated source code, runtime artifacts, build outputs, and data
- **New Structure**:
  - `runtime/` - All runtime artifacts (cache, logs, outputs) - gitignored
  - `data/` - Context, storage, sprints, templates (consolidated data)
  - `build/` - Build artifacts (archives, dashboard, static files)
  - `docs/admin/` - Administrative documentation
- **Path Updates**: Updated all hardcoded paths in memory engine and tools
- **Context Consolidation**: Merged `context-source/` and `context-store/` into `data/context/`

## Technical Constraints

### 1. API Limitations
- **OpenAI**: Rate limits and token constraints
- **Supabase**: Connection pooling and query limits
- **Vector DB**: Embedding dimension constraints

### 2. Performance Considerations
- **Memory Usage**: Vector storage can be memory-intensive
- **Disk Space**: Cache and storage growth over time
- **Network**: API dependency requires stable connectivity

### 3. Security Requirements
- **API Key Management**: Secure storage and rotation
- **Data Privacy**: PII detection and protection
- **Access Control**: Role-based permissions
- **Audit Compliance**: Complete operation logging
