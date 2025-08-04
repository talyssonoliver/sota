# Morning Briefing Generator - API Documentation

## Overview

The Morning Briefing Generator is part of Phase 6 Daily Automation & Visualization system. It provides comprehensive automated daily briefing generation with sprint status, task organization, and actionable insights using existing Phase 5 infrastructure.

## Features

### Core Functionality
- **Regular Briefings**: Generate morning, midday, and end-of-day briefings
- **Day-Specific Briefings**: Generate targeted briefings for specific sprint days
- **Multiple Output Formats**: Markdown, HTML, and console output
- **Task Categorization**: Automatic backend/frontend task separation
- **Sprint Health Assessment**: Real-time completion metrics and velocity tracking

### Integration
- **Phase 5 Metrics**: Leverages existing `CompletionMetricsCalculator`
- **Task Management**: Reads from task declaration and status files
- **Dashboard Integration**: Works with existing dashboard infrastructure
- **Email System**: Compatible with automated email distribution

## CLI Usage

### Day-Specific Briefing Generation

```bash
# Generate Day 2 briefing (markdown format, saved to file)
python orchestration/generate_briefing.py --day 2

# Generate Day 3 briefing with console output
python orchestration/generate_briefing.py --day 3 --format console

# Generate Day 1 briefing with markdown output
python orchestration/generate_briefing.py --day 1 --format markdown
```

### Regular Briefing Generation

```bash
# Generate morning briefing
python orchestration/generate_briefing.py --type morning

# Generate end-of-day briefing with HTML format
python orchestration/generate_briefing.py --type eod --format html

# Generate briefing without metrics
python orchestration/generate_briefing.py --no-metrics
```

## API Reference

### BriefingGenerator Class

#### Core Methods

##### `generate_day_briefing(day: int, output_format: str = "markdown")`
Generates day-specific morning briefing as required by Step 6.2.

**Parameters:**
- `day` (int): Day number for the briefing (must be positive)
- `output_format` (str): Output format ("markdown" or "console")

**Returns:**
- Dictionary with briefing data and status

**Example:**
```python
from orchestration.generate_briefing import BriefingGenerator

generator = BriefingGenerator()
result = await generator.generate_day_briefing(day=2)

if result["status"] == "success":
    print(f"Briefing saved to: {result['file_path']}")
```

##### `generate_briefing(briefing_type, include_metrics, include_priorities, output_format)`
Generates regular briefings with comprehensive sprint analysis.

**Parameters:**
- `briefing_type` (str): "morning", "midday", or "eod"
- `include_metrics` (bool): Include sprint metrics
- `include_priorities` (bool): Include task priorities
- `output_format` (str): "markdown", "html", or "console"

#### Data Gathering Methods

##### `_get_backend_tasks()`
Identifies and returns backend-specific tasks based on:
- Task ID prefix (`BE-`)
- Task type field (`backend`)
- Task title keywords (`backend`)

##### `_get_frontend_tasks()`
Identifies and returns frontend-specific tasks based on:
- Task ID prefix (`FE-`)
- Task type field (`frontend`)
- Task title keywords (`frontend`, `ui`)

##### `_generate_key_focus()`
Analyzes tasks to generate key focus areas for the day:
- Backend integration priorities (Supabase, services)
- Frontend development focus (components, UI alignment)
- Default momentum maintenance

##### `_generate_coordination_points(day: int)`
Creates time-based coordination points:
- Morning sync meetings (10:30 AM)
- Afternoon integration calls (1:30 PM)
- Day-specific events (sprint kickoff, progress reviews)

## Output Formats

### Day-Specific Briefing Structure

#### Markdown Format (`day{X}-morning-briefing.md`)
```markdown
# Day {X} Morning Briefing

## Backend Tasks
- BE-01: Validate Supabase Setup
- BE-02: Generate and Insert Seed Data
[...additional tasks]

## Frontend Tasks
- FE-01: Validate Local Environment Setup
- FE-02: Implement Core UI Components
[...additional tasks]

## Key Focus
- Backend to integrate services with Supabase
- Frontend to continue component development

## Coordination Points
- 10:30 AM Logs sync
- 1:30 PM API Integration call

---
*Generated at {timestamp} by Daily Automation System*
*Saved to: docs/sprint/briefings/day{X}-morning-briefing.md*
```

#### Console Format
```
============================================================
DAY {X} MORNING BRIEFING
============================================================
BACKEND TASKS:
  - BE-01: Validate Supabase Setup
  - BE-02: Generate and Insert Seed Data
  
FRONTEND TASKS:
  - FE-01: Validate Local Environment Setup
  - FE-02: Implement Core UI Components
  
KEY FOCUS:
  - Backend to integrate services with Supabase
  - Frontend to continue component development
  
COORDINATION POINTS:
  - 10:30 AM Logs sync
  - 1:30 PM API Integration call
============================================================
Generated at {timestamp}
============================================================
```

## File Structure

### Input Sources
- `tasks/*/task_declaration.json` - Task metadata and descriptions
- `tasks/*/status.json` - Current task status and state
- `dashboard/completion_metrics.json` - Sprint metrics data

### Output Files
- `docs/sprint/briefings/day{X}-morning-briefing.md` - Day-specific briefings
- `docs/sprint/briefings/{type}-briefing-{date}.md` - Regular briefings

## Error Handling

### Common Scenarios
- **Invalid day parameter**: Returns validation error for non-positive integers
- **Missing task data**: Gracefully handles missing declaration or status files
- **Metrics calculation failure**: Continues with warning, excludes metrics from output
- **File write errors**: Reports error but continues operation

### Logging
All operations are logged with appropriate levels:
- **INFO**: Successful operations and status updates
- **WARNING**: Non-critical issues (missing metrics, task data)
- **ERROR**: Critical failures requiring attention

## Integration Examples

### Daily Automation Cycle
```python
from orchestration.daily_cycle import DailyCycleOrchestrator

orchestrator = DailyCycleOrchestrator()
morning_result = await orchestrator.run_morning_briefing()
```

### Custom Briefing Generation
```python
from orchestration.generate_briefing import BriefingGenerator

generator = BriefingGenerator()

# Generate multiple days
for day in range(1, 4):
    result = await generator.generate_day_briefing(day=day)
    print(f"Day {day}: {result['status']}")
```

## Testing

### Test Coverage
The briefing generator has comprehensive test coverage in `tests/test_generate_briefing.py`:
- Day-specific briefing generation
- Output format validation
- Error handling scenarios
- Task categorization logic
- File saving operations

### Running Tests
```bash
# Run briefing generator tests
python -m pytest tests/test_generate_briefing.py -v

# Run all Phase 6 automation tests
python -m pytest tests/test_phase6_automation.py -v
```

## Configuration

### Dependencies
- `utils.completion_metrics.CompletionMetricsCalculator`
- `utils.execution_monitor.ExecutionMonitor`
- Task declaration and status files
- Briefings output directory (`docs/sprint/briefings/`)

### Requirements
- Python 3.8+
- Existing Phase 5 infrastructure
- Task management structure
- Write permissions to output directory

## Support

For issues or questions:
1. Check existing test suite for examples
2. Review Phase 6 automation documentation
3. Verify Phase 5 infrastructure status
4. Check file permissions and directory structure

---

**Part of Phase 6 Daily Automation & Visualization - Mission Accomplished ✅**
