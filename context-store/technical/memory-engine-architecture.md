# Memory Engine Architecture
**Reviewed: Not yet reviewed**

## Overview

The Memory Engine implements the Model Context Protocol (MCP) and serves as the knowledge management system for the AI Agent System, providing relevant context to agents during task execution.

## Core Components

### Vector Database
- Uses ChromaDB for vector storage and retrieval
- Embeddings generated using OpenAI embeddings model
- Organized collections for different knowledge domains

### Document Processing
- Chunking mechanism for breaking large documents into digestible pieces
- Metadata tagging for improved filtering and retrieval
- Automatic summarization for large documents

### Context Retrieval
- Semantic search based on vector similarity
- Key-based direct document access
- Filtered retrieval based on metadata

### Integration Interface
- Memory interface for agent integration
- Context injection into agent prompts
- Document storage and indexing

## Key Functionalities

### Store Context
```python
memory.store_context(
    content="The Artesanato E-commerce platform uses Supabase for authentication.",
    metadata={"source": "technical/architecture.md", "type": "architecture"}
)
```

### Retrieve Context via Vector Search
```python
context = memory.retrieve_context(
    query="What authentication system does the platform use?",
    n_results=3
)
```

### Retrieve Context via Key-Based Lookup
```python
context = memory.get_context_by_keys(["db-schema", "service-pattern"])
```

### Document Processing
```python
# Process raw documents from context-source/ into summarized context-store/ documents
memory.scan_and_summarize(source_dirs=["context-source/"], summary_dir="context-store/")
```

## Document Organization

The Memory Engine organizes knowledge in:

1. **Source Documents** (`context-source/`)
   - Raw, unprocessed documentation
   - Organized by domain (db, infra, design, patterns, etc.)
   
2. **Processed Summaries** (`context-store/`)
   - Concise, agent-optimized summaries
   - Organized by domain for targeted retrieval

## Memory Flow

1. Source documents are collected in `context-source/` directory
2. Documents are processed into summaries in `context-store/`
3. Summaries are indexed into the vector database
4. Agents request context via semantic search or direct key lookup
5. Relevant context is injected into agent prompts

## Related Components
- [Agent System Architecture](agent-system-architecture.md)
- [LangGraph Workflow Architecture](langgraph-workflow-architecture.md)
- [Tool System Architecture](tool-system-architecture.md)

---
*Drafted by doc_agent on May 16, 2025. Technical lead: please review for accuracy and completeness.*