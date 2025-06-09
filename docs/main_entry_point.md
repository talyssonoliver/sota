# Main Entry Point Documentation

**File:** `main.py`
**Type:** entry point / test harness
**Purpose:** Runs basic setup tests for the AI Agent System to verify that tools and workflow components work correctly. It loads environment variables, applies patch fixes, and then executes a series of small tests for the Echo tool, Supabase tool, Memory Engine, and a simplified LangGraph workflow.

## Imports
- `os`, `sys`: standard libraries for environment access and exiting.
- `dotenv.load_dotenv`: loads environment variables from `.env`.
- `patches.apply_all_patches`: applies compatibility patches for external libraries if available.
- `langchain.agents.initialize_agent`, `langchain.agents.AgentType`, `langchain.tools.Tool`: used for creating simple test agents.
- `langchain_community.chat_models.ChatOpenAI`: language model interface.
- `graph.flow.build_workflow_graph`: workflow builder (not used directly in the tests but imported for reference).
- `tools.echo_tool.EchoTool`: simple echo utility used in `run_simple_agent_test`.
- `tools.supabase_tool.SupabaseTool`: database schema retrieval tool used in `run_supabase_tool_test`.
- `tools.memory_engine.get_relevant_context`, `tools.memory_engine.memory`: functions for context retrieval and memory initialization.

## Environment Setup
1. `load_dotenv()` loads variables from `.env`.
2. Reads `OPENAI_API_KEY` from the environment. If missing, prints an error and exits.
3. Applies patches via `apply_all_patches()` if the `patches` module is available.

## Functions
### `run_simple_agent_test()`
Runs a simple LangChain agent with the Echo tool.
```python
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k")
echo_tool = EchoTool()
agent = initialize_agent(
    tools=[Tool.from_function(
        func=echo_tool._run,
        name=echo_tool.name,
        description=echo_tool.description
    )],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
result = agent.invoke({"input": "Use the echo tool to repeat 'Phase 0 setup complete'"})
print("Result:", result['output'])
```
Returns: none (prints output to console).

### `run_supabase_tool_test()`
Creates a LangChain agent using `SupabaseTool` to fetch the database schema.
Prints the result returned by the agent.

### `run_memory_test()`
Calls `get_relevant_context()` from the Memory Engine with a fixed query and prints the retrieved context.

### `run_workflow_test()`
Builds a minimal LangGraph `StateGraph` with a single `test_handler` node that echoes success information. Invokes the compiled graph with a test state and prints the result.

## Execution Flow
When the script is run directly:
1. Prints a header message.
2. Calls each of the four test functions in sequence.
3. Prints completion messages after all tests succeed.

## Next Critical Modules
Execution of this file references several other important modules:
- `tools/echo_tool.py` – implementation of the Echo tool.
- `tools/supabase_tool.py` – integration with Supabase for schema retrieval.
- `tools/memory_engine.py` – core memory system for context lookup.
- `graph/flow.py` – defines the LangGraph workflow logic.
These modules form the next logical targets for documentation in future sessions.
