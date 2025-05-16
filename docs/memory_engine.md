# Memory Engine (MCP)

This document describes the Memory Engine component of the AI Agent System, which implements the Model Context Protocol (MCP).

## Overview

The Memory Engine is a critical component that provides agents with relevant context from the knowledge base. It uses vector embeddings to retrieve information that is most relevant to the current task, and now supports direct key-based document retrieval for more targeted context access.

## Implementation

The Memory Engine is implemented in `tools/memory_engine.py` and provides several key capabilities:

1. Context storage and embedding
2. Semantic search across knowledge base
3. Retrieval of relevant information for agents
4. Context summarization and condensation
5. Direct key-based access to specific memory documents

## Key Features

### Vector-Based Retrieval
Searches the entire knowledge base for contextually relevant information using vector embeddings and semantic similarity.

### Key-Based Document Retrieval
Provides direct access to specific memory documents by their keys (filename without extension), allowing for targeted context injection without vector search overhead.

### Modular Context Design
Memory files are stored in a modular fashion, allowing agents to receive only the context relevant to their current task.

## API Reference

### Initializing the Memory Engine

```python
from tools.memory_engine import MemoryEngine

memory = MemoryEngine(
    knowledge_base_path="context-store/",
    embedding_model="text-embedding-3-small"
)
```

### Storing Context

```python
memory.store_context(
    content="The Artesanato E-commerce platform uses Supabase for database and authentication.",
    metadata={"source": "technical/architecture.md", "type": "architecture"}
)
```

### Retrieving Context via Vector Search

```python
context = memory.retrieve_context(
    query="What database system does the platform use?",
    n_results=3
)
```

### Retrieving Context via Key-Based Lookup

```python
# New key-based context retrieval
context = memory.get_context_by_keys(["db-schema", "service-pattern"])
```

### Context Search

```python
search_results = memory.search(
    query="authentication system",
    filters={"type": "architecture"},
    n_results=5
)
```

### Bulk Loading Context

```python
memory.load_directory("context-store/backend/")
```

## Integration with Agents

The Memory Engine is integrated with agents to provide relevant context during task execution.

### Vector-Based Integration

```python
# Inside an agent's execution
def execute_task(self, task):
    context = self.memory.retrieve_context(f"Information about {task}")
    # Use context to inform the agent's response
    return self.generate_response(task, context)
```

### Key-Based Integration (New)

```python
# Using the new key-based context retrieval
from tools.memory_engine import get_context_by_keys

def create_backend_engineer_agent(context_keys=None):
    if context_keys is None:
        context_keys = ["db-schema", "service-pattern"]
        
    # Get MCP context directly from specified document keys
    mcp_context = get_context_by_keys(context_keys)
    
    return Agent(
        role="Supabase Engineer",
        goal="Implement robust API services",
        system_prompt=load_and_format_prompt(
            "prompts/backend-agent.md", 
            context=mcp_context
        )
    )
```

## Memory Structure

The Memory Engine organizes information in two main ways:

1. **Vector Database**
   - Content: The actual information to be stored
   - Embeddings: Vector representations of the content
   - Metadata: Additional information about the content (source, type, etc.)
   - Timestamps: When the information was added or updated

2. **File-Based Documents** (New)
   - Stored in the `context-store/` directory
   - Named with meaningful keys (e.g., `db-schema-summary.md`, `service-pattern.md`)
   - Accessed directly by key through `get_context_by_keys()` function
   - Primarily in Markdown format for human readability

## Directory Structure

```
context-store/
├── \db\db-schema-summary.md          # Database schema information
├── service-pattern.md     # Backend service patterns
├── component-patterns.md  # Frontend component patterns
├── testing-strategy.md    # QA testing strategies
└── ...
```

## Optimizations

The Memory Engine includes several optimizations:

1. **Caching**: Frequently accessed context is cached for faster retrieval
2. **Chunking**: Large documents are split into smaller chunks for more precise retrieval
3. **Semantic Reranking**: Results are reranked based on semantic relevance to the query
4. **Context Windowing**: Only the most relevant context is included in responses
5. **Direct Document Access**: Bypasses vector search for known document keys, improving performance
6. **Task-Specific Context**: Only provides context relevant to the specific task domain

## Best Practices

1. **Use Key-Based Retrieval When Possible**: For known document types, use direct key access
2. **Organize by Domain**: Store context documents in domain-specific categories
3. **Be Specific in Queries**: When using vector search, be as specific as possible
4. **Include Metadata**: Add metadata to context to enable filtering
5. **Update Regularly**: Keep the knowledge base updated with the latest information
6. **Monitor Usage**: Track which contexts are most frequently retrieved to optimize the knowledge base
7. **Keep Documents Focused**: Each document should focus on a specific topic or domain

## Configuration

The Memory Engine can be configured through the following parameters:

- `knowledge_base_path`: Path to the knowledge base directory
- `embedding_model`: Model to use for generating embeddings
- `similarity_threshold`: Minimum similarity score for context retrieval
- `chunk_size`: Size of chunks for splitting documents
- `chunk_overlap`: Overlap between chunks
- `cache_size`: Size of the context cache