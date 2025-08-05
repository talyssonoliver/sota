# Daily Cycle Orchestrator Documentation

**File:** `orchestration/daily_cycle.py`
**Type:** workflow orchestrator
**Purpose:** Automates the daily workflow of generating briefings, progress checks and end-of-day reports. It schedules recurring tasks, manages dashboard updates and handles email notifications.

## Key Components
- `DailyCycleOrchestrator` class – central orchestrator for daily automation
- `CompletionMetricsCalculator` – calculates team metrics
- `ExecutionMonitor` – tracks workflow executions
- `BriefingGenerator` and `EndOfDayReportGenerator` – produce reports
- `EmailIntegration` – optional email delivery

## Initialization
```python
class DailyCycleOrchestrator:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/daily_cycle.json"
        self.config = self._load_config()
        self._setup_logging()
        self.metrics_calculator = CompletionMetricsCalculator()
        self.execution_monitor = ExecutionMonitor()
        self.briefing_generator = BriefingGenerator()
        self.eod_report_generator = EndOfDayReportGenerator()
        self.email_integration = EmailIntegration(self.config_path)
```
The constructor loads configuration, sets up logging and instantiates helper classes.

## Configuration Loader
The private `_load_config()` method merges `config/daily_cycle.json` with defaults:
```python
    def _load_config(self) -> Dict[str, Any]:
        default_config = self._get_default_config()
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            merged = default_config.copy()
            for section, values in loaded.items():
                if section in merged and isinstance(values, dict):
                    merged[section].update(values)
                else:
                    merged[section] = values
            return merged
        return default_config
```
It returns a dictionary used throughout the orchestrator.

## Core Methods
### `run_morning_briefing()`
Generates a morning briefing, optionally emails it and refreshes the dashboard. Returns a status dict.

### `run_midday_check()`
Calculates metrics, generates a progress report and logs completion.

### `run_end_of_day_report()`
Produces an enhanced end-of-day report and a traditional report, then emails and updates the dashboard.

### `schedule_enhanced_tasks()`
Schedules all recurring tasks using the `schedule` library. It sets morning briefings, EOD reports and optional midday checks, plus health monitoring and dashboard updates.

### `start_scheduler()`
Runs the scheduling loop, executing pending jobs and handling errors until interrupted.

### `run_manual_cycle(cycle_type)`
Allows running a single cycle via CLI arguments for testing (`full`, `morning`, `midday`, `eod`).

### Health and Performance
- `run_health_check()` – checks status of key components and optional dashboard API
- `run_performance_check()` – gathers CPU, memory and log directory metrics
- `run_emergency_stop()` – cancels all jobs and sends an emergency notification

## CLI Usage
The module exposes a `main()` function for command line execution. Example:
```bash
python orchestration/daily_cycle.py --mode schedule
```
Options allow manual runs, health checks and enabling weekend mode.

