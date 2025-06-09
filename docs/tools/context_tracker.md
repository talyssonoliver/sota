# context_tracker.py

Provides utilities for tracking which memory documents were used for each task.
Context usage is stored under `outputs/<task_id>/context_log.json` and later
aggregated for reporting.

## Key Functions

- **`track_context_usage(task_id, context_topics, documents_used, ...)`** – save
  a log entry describing which documents were retrieved for a task.
- **`get_context_log(task_id)`** – load the log for a specific task.
- **`get_all_context_logs()`** – return logs for every task found in the
  `outputs` directory.
- **`analyze_context_usage(task_ids=None)`** – produce frequency statistics of
  topics and documents used.
- **`export_context_usage_report(path)`** – export a combined report (used in
  Step 3.7).
- **`track_context_from_memory_engine()`** – helper that integrates with the
  `MemoryEngine` to automatically log retrieved documents.

These utilities support detailed reporting and metrics around how much context
each agent consumes when executing tasks.
