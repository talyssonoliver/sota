# memory_engine_examples.py

This helper module contains example functions demonstrating how to use the
`MemoryEngine` API. It is primarily intended for developers exploring the memory
subsystem.

## Examples

- **`index_knowledge_with_chroma()`** – load documents from `context-store/` and
  index them into a Chroma collection.
- **`add_document_example()`** – show how to add a single file with metadata.
- **`initialize_and_search_example()`** – configure the engine and perform a
  vector search.

Each function can be run directly from the command line:

```bash
python tools/memory_engine_examples.py index
```
