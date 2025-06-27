# Compatibility Modules

This directory contains compatibility layers for external libraries that may not be installed in all environments.

## Purpose

These modules provide mock implementations and compatibility interfaces for:

- **LangChain** (`langchain/`, `langchain_core/`) - Chain and runnable interfaces
- **ChromaDB** (`chromadb/`) - Vector database API models
- **Test utilities** - Testing framework compatibility

## Usage

The compatibility modules are automatically added to the Python path when imported:

```python
import sys
sys.path.insert(0, 'tools/compatibility')

# Now you can use the compatibility modules
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.runnables import Runnable
from chromadb.api.models import Document
```

## Automatic Setup

For automatic setup, use the setup script:

```python
from tools.compatibility.setup_compatibility import initialize_compatibility
initialize_compatibility()
```

## Features

- **Drop-in replacements** for external library interfaces
- **Functional implementations** (not just mocks) where possible
- **Graceful degradation** when real libraries are unavailable
- **No external dependencies** required

## File Structure

```
tools/compatibility/
├── README.md                 # This file
├── __init__.py              # Package initialization
├── setup_compatibility.py   # Automatic setup script
├── chromadb/               # ChromaDB compatibility
│   ├── __init__.py
│   └── api/
│       ├── __init__.py
│       └── models.py
├── langchain/              # LangChain compatibility
│   ├── __init__.py
│   └── chains/
│       └── retrieval_qa/
│           ├── __init__.py
│           └── base.py
└── langchain_core/         # LangChain Core compatibility
    ├── __init__.py
    └── runnables.py
```

This ensures the codebase can run even when external AI/ML libraries are not installed.