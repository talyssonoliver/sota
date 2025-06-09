# jest_tool.py

Utility for running JavaScript unit tests with Jest. It can generate test
templates and execute existing test suites in the frontend project.

## JestTool class

Features include:
- ` _run("run")` – execute `npm test` inside the configured project path.
- ` _run("template")` – return an example Jest test case.
- Integration with `ArtesanatoBaseTool` for standardized responses.

Example:

```python
jest = JestTool(project_path="./frontend")
result = jest.call("run")
```
