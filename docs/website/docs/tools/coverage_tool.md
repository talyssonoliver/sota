# coverage_tool.py

The **CoverageTool** allows agents to inspect test coverage reports and enforce
coverage thresholds. It provides commands for generating coverage summaries,
checking or setting thresholds, and identifying files with poor coverage.

## CoverageTool class

```python
class CoverageTool(ArtesanatoBaseTool):
    """Analyze and report on test coverage."""

    def _run(self, query: str) -> str:
        # Parse the query and perform the requested operation
        if "get report" in query:
            return self._get_coverage_report(...)
        elif "check thresholds" in query:
            return self._check_coverage_thresholds()
        ...
```

### Important Operations

- `get report format:summary path:src/` – return overall coverage numbers.
- `check thresholds` – validate if current coverage meets stored thresholds.
- `set thresholds lines:80 branches:70` – update minimum acceptable coverage.
- `identify gaps path:src/components` – list files with metrics below threshold.

The tool returns structured JSON with data, error messages, and metadata so that
agents can easily interpret the results.
