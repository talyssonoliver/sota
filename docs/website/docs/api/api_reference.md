# API Reference

The dashboard exposes a small set of HTTP endpoints implemented with Flask.

## Unified Dashboard API
File: `dashboard/unified_api_server.py`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check endpoint |
| GET | `/api/metrics` | Retrieve aggregated metrics |
| POST | `/api/metrics/refresh` | Trigger metrics recalculation |
| GET | `/dashboard/` | Serve dashboard index page |
| GET | `/dashboard/<filename>` | Serve static dashboard asset |
| GET | `/legacy/<filename>` | Serve legacy dashboard asset |
| GET | `/api/sprint/health` | Sprint progress report |
| GET | `/api/tasks/recent` | Recent task history |
| GET | `/api/automation/status` | Automation status details |
| GET | `/api/progress/trend` | Trend data for progress over time |

## Gantt Chart API
File: `dashboard/gantt_api.py` – registered under `/api/gantt`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/gantt/data` | Gantt chart dataset |
| GET | `/api/gantt/critical-path` | Critical path analysis |
| GET | `/api/gantt/resources` | Resource allocation data |
| GET | `/api/gantt/recommendations` | Suggested schedule adjustments |
| POST | `/api/gantt/optimize` | Optimize timeline |
| PUT | `/api/gantt/tasks/<task_id>` | Update task information |
| GET | `/api/gantt/export/<format_type>` | Export Gantt data in specified format |

