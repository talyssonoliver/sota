# AI Agent System for Artesanato E-commerce

This project implements a **multi-agent AI system** that automates software development tasks for the Artesanato E-commerce platform. It leverages specialized agents (Technical Lead, Backend, Frontend, QA, Documentation, etc.), each focused on a specific role, coordinated through a LangGraph-based workflow engine. The system uses CrewAI for agent logic, LangChain/LangGraph for orchestration, and a vector database (ChromaDB) for context-aware operations.

## Overview

The system uses specialized agents for different roles (Technical Lead, Backend Engineer, Frontend Engineer, etc.) to complete pre-Sprint 0 tasks. It follows these design principles:

- **MCP (Model Context Protocol)**: Provides agents with relevant context from the knowledge base
- **A2A (Agent-to-Agent Protocol)**: Enables structured communication between agents
- **LangGraph**: Defines workflows as directed graphs with agents as nodes
- **CrewAI**: Creates role-specialized agents with distinct capabilities
- **Dynamic Workflow**: Adapts to task requirements and dependencies, allowing for flexible execution paths
- **Task Orchestration**: Manages task execution order based on dependencies, ensuring efficient resource utilization
- **LangSmith**: Unifies observation and testing for all agents, providing a consistent interface for monitoring and debugging
- **Tool Loader**: Loads and configures tools for each agent, enabling them to perform specialized tasks
- **Tool Integration**: Connects agents to external tools (e.g., Supabase, GitHub) for enhanced functionality
- **Testing Framework**: Provides a unified test runner for validating agent functionality and system integration
- **Documentation**: Generates comprehensive reports and documentation for each task, ensuring transparency and traceability
- **Progress Tracking**: Monitors task completion and generates reports for each sprint cycle


## Project Structure

```
ai-system/
├── agents/
│   ├── __init__.py
│   ├── backend.py
│   ├── coordinator.py
│   ├── doc.py
│   ├── frontend.py
│   ├── qa.py
│   └── technical.py
│
├── config/
│   ├── agents.yaml
│   ├── tools.yaml
│   └── schemas/
│       └── task.schema.json
│
├── context-store/
│   └── (summaries, patterns, db schema, etc.)
│
├── graph/
│   ├── auto_generate_graph.py
│   ├── flow.py
│   ├── graph_builder.py
│   ├── handlers.py
│   ├── notifications.py
│   ├── resilient_workflow.py
│   └── visualize.py
│
├── orchestration/
│   ├── delegation.py
│   ├── enhanced_workflow.py
│   ├── execute_graph.py
│   ├── execute_task.py
│   ├── execute_workflow.py
│   ├── generate_prompt.py
│   ├── inject_context.py
│   ├── registry.py
│   └── run_workflow.py
│
├── prompts/
│   └── utils.py
│
├── scripts/
│   ├── list_pending_reviews.py
│   ├── mark_review_complete.py
│   ├── monitor_workflow.py
│   ├── patch_dotenv.py
│   ├── test_sprint_phases.py
│   └── visualize_task_graph.py
│
├── tasks/
│   └── *.yaml (individual task YAML files)
│
├── tests/
│   ├── mock_environment.py
│   ├── run_tests.py
│   ├── test_agent_orchestration.py
│   ├── test_agents.py
│   ├── test_enhanced_workflow.py
│   ├── test_memory_config.py
│   ├── test_qa_agent_decisions.py
│   ├── test_utils.py
│   ├── test_workflow_integration.py
│   └── test_workflow_states.py
│   └── test_outputs/
│       ├── BE-07/
│       │   ├── error.log
│       │   ├── output_unknown.md
│       │   └── status.json
│       ├── FE-01/
│       │   ├── error.log
│       │   ├── output_unknown.md
│       │   └── status.json
│       ├── QA-01/
│       │   ├── error.log
│       │   ├── output_unknown.md
│       │   └── status.json
│       └── TL-01/
│           ├── error.log
│           ├── output_unknown.md
│           └── status.json
│
├── tools/
│   ├── __init__.py
│   ├── base_tool.py
│   ├── coverage_tool.py
│   ├── cypress_tool.py
│   ├── design_system_tool.py
│   ├── echo_tool.py
│   ├── github_tool.py
│   ├── jest_tool.py
│   ├── markdown_tool.py
│   ├── memory_engine.py
│   ├── supabase_tool.py
│   ├── tailwind_tool.py
│   ├── tool_loader.py
│   └── vercel_tool.py
│
├── utils/
│   ├── add_schemas_to_tasks.py
│   ├── fix_yaml_schema.py
│   ├── fix_yaml_schemas.py
│   ├── migrate_tasks.py
│   ├── review.py
│   └── task_loader.py
│
├── _FILE_RELATIONSHIPS.json
├── _LLM_INSTRUCTIONS.md
├── _PROJECT_SUMMARY.md
├── main.py
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.template` to `.env` and add your API keys:
   ```bash
   cp .env.template .env
   # Edit .env to add your API keys
   ```

## Usage

### Testing the Setup

Run the setup tests to verify all components are working:

```bash
python main.py
```

### Running a Task

To run a specific task:

```bash
python orchestration/execute_task.py --task TL-01
```

### Using the LangGraph Workflow

The system uses a dynamic workflow graph built with LangGraph that coordinates agents as nodes in a DAG (Directed Acyclic Graph). The workflow is defined in `graph/critical_path.yaml` and can be executed using the workflow runner:

```bash
# Run a single task through the LangGraph workflow
python orchestration/execute_workflow.py --task BE-07

# Run all tasks in dependency order
python orchestration/execute_workflow.py --all

# Run tasks for a specific agent
python orchestration/execute_workflow.py --agent backend_engineer

# Run tasks for a specific day
python orchestration/execute_workflow.py --day 2

# Use dynamic workflow routing for more adaptive execution
python orchestration/execute_workflow.py --all --dynamic

# Specify a custom output directory
python orchestration/execute_workflow.py --all --output "reports/sprint1"
```

The workflow automatically:
- Maps each agent's role to a node in the graph
- Defines edges based on task dependencies in the critical path
- Executes tasks in dependency order
- Generates comprehensive execution reports

### Daily Operations

To start a day's workflow:

```bash
python orchestration/daily_cycle.py --day 1 --start
```

To generate an end-of-day report:

```bash
python orchestration/daily_cycle.py --day 1 --end
```

## Testing

The system includes comprehensive testing for agents, tools, and orchestration using a unified test runner:

### Running Tests

The test system uses a unified test runner that can execute different test suites:

```bash
# Run all tests (quick validation, tool tests, and full suite)
python -m tests.run_tests --all

# Run only the quick validation test (fastest option)
python -m tests.run_tests --quick

# Run only the tool loader tests
python -m tests.run_tests --tools

# Run only the full test suite
python -m tests.run_tests --full

# Show available test options
python -m tests.run_tests --help
```

### Test Components

- **run_tests.py**: Unified test runner with multiple test modes
- **mock_environment.py**: Utility for patching external dependencies
- **test_agents.py**: Unit tests for agent instantiation and setup
- **test_agent_orchestration.py**: Tests for agent delegation and task routing
- **test_tool_loader.py**: Tests for tool configuration and loading

The test system uses dependency mocking to ensure tests can run without requiring external API keys or services.

## System Components

### Memory Engine (MCP)

Located in `tools/memory_engine.py`, this component provides relevant context to agents using vector embeddings.

### Workflow Graphs (A2A)

The system has two main workflow components:

1. **Basic Flow Definitions**: Located in `graph/flow.py`, these define how agents communicate and pass messages.

2. **Dynamic LangGraph Builder**: Located in `graph/graph_builder.py`, this builds workflow graphs by:
   - Loading configuration from `critical_path.yaml`
   - Creating nodes from registered agents
   - Setting up dependencies as graph edges
   - Providing dynamic routing based on task characteristics

The workflow graphs enable:
- Dependency-based task execution
- Parallel processing of independent tasks
- Dynamic adaptation to task requirements
- Comprehensive execution reporting

### Agent Definitions

Configured in `config/agents.yaml`, with prompt templates in the `prompts/` directory.

### Tools

Custom tools in the `tools/` directory provide agents with capabilities like database querying and code generation.

## License

MIT License. See `LICENSE` for details.