# Utility Functions Catalog

This catalog groups the most frequently used utilities found under the `utils/` directory.
Only the most impactful modules are summarized here.

## Task Management Utilities

- **`task_loader.py`** – Load, save, and query task metadata from YAML files.
- **`migrate_tasks.py`** – Move existing tasks to the latest schema version.
- **`workflow_recursion_fix.py`** – Patch workflow logic to avoid infinite loops during execution.

## Metrics & Analysis

- **`completion_metrics.py`** – Track code completion progress and generate reports.
- **`coverage_analyzer.py`** – Produce code coverage summaries for QA.
- **`integration_analyzer.py`** – Inspect integration tests and log missing cases.

## Monitoring & Feedback

- **`execution_monitor.py`** – Centralized logging helper for workflow execution.
- **`feedback_system.py`** – Collect and store user feedback from completed tasks.
- **`escalation_system.py`** – Notify maintainers when tasks exceed risk thresholds.

These utilities support day‑to‑day operations and are typically invoked by agents or orchestration scripts. For additional helpers, browse the `utils/` directory directly.
