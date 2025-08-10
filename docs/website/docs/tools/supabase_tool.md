# supabase_tool.py

Interface for interacting with a Supabase database. The tool can execute SQL
queries, fetch schema details, and provide service pattern examples used by the
backend agent.

## SupabaseTool class

Main features:
- Initializes a Supabase client using `SUPABASE_URL` and `SUPABASE_KEY` from the
  environment (falls back to mock mode if missing).
- Provides `_run` operations for "get schema", "execute query", and retrieving
  service pattern templates.
- Returns structured JSON with query results or error information.

Example usage:

```python
tool = SupabaseTool()
result = tool.call("get schema")
schema = result["data"]
```
