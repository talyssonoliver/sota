# scripts/mock_dependencies.py

## Classes
- **MockLiteLLM** (line 9)
- **MockOpenAIEmbeddings** (line 117)
  - Methods: __init__, embed_documents, embed_query
- **MockChroma** (line 134)
  - Methods: __init__, similarity_search, add_texts, add_documents, from_texts
- **MockLangChainBaseTool** (line 160)
  - Methods: __init__, _run, run
- **MockRender** (line 184)
  - Methods: format_tool_to_openai_function, render_text_description_and_args
- **MockDirectoryLoader** (line 208)
  - Methods: __init__, load

## Functions
- **patch_imports()** (line 220)
