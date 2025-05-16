# Memory Engine (MCP) Summary
**Reviewed: Not yet reviewed**

## Core Functionality
- Provides agents with relevant context from knowledge base
- Implements Model Context Protocol (MCP) for knowledge retrieval
- Supports both vector-based and key-based document retrieval
- Located in tools/memory_engine.py

## Key Features
- **Vector-Based Retrieval**: Uses embeddings for semantic similarity search
- **Key-Based Document Retrieval**: Direct access to specific documents by key
- **Modular Context Design**: Structured by domain for targeted relevance
- **Context Summarization**: Condenses large documents when needed
- **Document Processing**: Handles document scanning, chunking, and embedding

## API Methods
- **store_context()**: Adds new information to the knowledge base
- **retrieve_context()**: Gets relevant information via vector search
- **get_context_by_keys()**: Retrieves specific documents by key
- **search()**: Performs filtered searches with metadata
- **load_directory()**: Bulk loads context from a directory
- **summarize_document()**: Creates concise summaries of long documents
- **index_summaries()**: Indexes all summaries into the vector store
- **scan_and_summarize()**: Processes source docs into structured summaries
- **get_filtered_context()**: Retrieves context with metadata filtering

## Integration Pattern
```python
# Using key-based retrieval in agent creation
mcp_context = get_context_by_keys(["db-schema", "service-pattern"])
agent = Agent(system_prompt=format_prompt(context=mcp_context))

# Automatic document processing workflow
memory.scan_and_summarize(source_dir="context-source/", summary_dir="context-store/")
memory.index_summaries("context-store/")
```

## Directory Organization
```
context-store/
├── db/db-schema-summary.md      # Database information
├── patterns/service-pattern.md  # Implementation patterns
├── technical/                   # Technical documentation
└── sprint/                      # Sprint information
```

## Best Practices
- Use key-based retrieval for known document types
- Organize context by domain in context-store/
- Keep documents focused on specific topics
- Update knowledge base regularly
- Use specific queries for vector search
- Apply metadata filtering for targeted results

---
*Drafted by doc_agent on May 16, 2025. Technical lead: please review for accuracy and completeness.*