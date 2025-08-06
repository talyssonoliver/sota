# echo_tool.py

The **EchoTool** provides a trivial example of a tool implementation. It simply
returns whatever text is passed to it and is used in the entry point tests to
verify that the tool system and agents are functioning correctly.

## EchoTool class

```python
class EchoTool(ArtesanatoBaseTool):
    """A simple tool that echoes back the input."""

    name: str = "echo_tool"
    description: str = "A simple tool that echoes back the input."

    def _run(self, query: str) -> str:
        try:
            validated = self.InputSchema(query=query)
            return f"ECHO: {validated.query}"
        except ValidationError as ve:
            return self.handle_error(ve, f"{self.name}._run.input_validation")
```

### Usage

```python
from tools.echo_tool import EchoTool

tool = EchoTool()
result = tool.call("hello")
print(result["data"])  # -> "ECHO: hello"
```
