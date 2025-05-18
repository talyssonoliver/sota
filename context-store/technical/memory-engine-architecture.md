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

## ChromaDB Partitioning, Hybrid Search, and Security Enhancements

- **Partitioning**: The Memory Engine now segments the vector database by document type, knowledge domain, and time relevance. A PartitionManager routes queries and manages cross-partition search and health.
- **Advanced Metadata Filtering**: Metadata schema includes agent role tags, domain, time markers, and reliability scores. Compound queries leverage ChromaDB's metadata filtering.
- **Reindexing**: Automatic reindexing is triggered by configurable thresholds and runs during low-usage periods, preserving data and optimizing index structures.
- **Hybrid Search**: Combines vector similarity and keyword (BM25/sparse) search with custom weighting and fallback mechanisms.
- **Similarity Search Tuning**: hnsw_ef_search and other parameters are dynamically tuned based on query importance and benchmarking.

## Performance and Caching

- **Multi-Tiered Caching**: L1 in-memory and L2 disk-based caches with analytics, preloading, and configurable policies. Hit/miss rates and memory usage are tracked.
- **Optimized Chunking**: Semantic and adaptive chunking with overlap, deduplication, and quality metrics. Chunking is content-aware and reduces index bloat.
- **Adaptive Retrieval**: Dynamic k, similarity thresholds, token budgets, and intent classification. Progressive retrieval and non-blocking async operations.
- **Resource Management**: Memory profiling, async processing, throttling, and prioritization. Tiered storage (hot/warm/cold) with automatic migration.

## Security and Compliance

- **Input Protection**: Robust sanitization, source verification, and content safety filters. Rate limiting and trust scoring for updates.
- **Access Control**: Role-based and attribute-based permissions, time-bound and purpose-limited access, secure delegation, and audit logging.
- **Data Protection**: At-rest and field-level encryption, key rotation, integrity verification, and secure deletion.
- **Audit and Lifecycle**: Detailed activity logging, log integrity, real-time alerting, retention policies, right-to-be-forgotten, PII detection, and leakage prevention.

## Configuration and API

- All features are configurable via a unified config object. Sensible defaults and validation are provided. The API remains backwards compatible, with deprecation warnings for any changes.

---
*Drafted by doc_agent on May 16, 2025. Technical lead: please review for accuracy and completeness. Updated for production-readiness, scalability, security, and performance. See `tools/memory_engine.py` for implementation details.*