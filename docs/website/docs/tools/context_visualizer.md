# context_visualizer.py

Generates reports and visualizations that show how memory context is used across
tasks. Builds on the logs produced by `context_tracker.py`.

## Main Functions

- **`analyze_context_coverage()`** – aggregate statistics about topics and
  documents across all tasks.
- **`generate_csv_report(data, path)`** – output a CSV summary of topic usage.
- **`generate_html_report(data, path)`** – create an interactive Plotly heatmap
  showing which tasks used which topics.
- **`generate_json_report(data, path)`** – dump analysis results as JSON.
- **`generate_context_coverage_report(format)`** – convenience wrapper used by
  the CLI to produce CSV and HTML reports in one go.

Example:

```bash
python tools/context_visualizer.py --format both
```
