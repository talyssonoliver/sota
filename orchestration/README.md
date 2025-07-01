# Orchestration Directory

## Purpose
This directory contains **production-ready CLI tools and interactive workflows** for the AI system. These implementations are designed for human interaction and command-line execution.

## When to Use This Directory
- Running workflows from the command line
- Interactive task execution and monitoring
- Human-in-the-loop operations
- Full-featured implementations with logging and progress tracking
- Production deployment of the AI system

## Key Components

### Workflow Execution
- `execute_workflow.py` - Main workflow execution engine
- `execute_task.py` - Individual task execution
- `execute_graph.py` - Graph-based workflow execution

### Task Management
- `task_declaration.py` - Full task declaration and management system
- `task_lifecycle.py` - Complete task lifecycle management
- `complete_task.py` - Task completion workflows

### Quality Assurance
- `qa_execution.py` - Complete QA execution engine (15KB)
- `qa_validation.py` - QA validation workflows
- `review_task.py` - Task review processes

### Analysis and Reporting
- `gantt_analyzer.py` - Complete Gantt chart analysis (49KB)
- `generate_briefing.py` - Full briefing generator with metrics (35KB)
- `end_of_day_report.py` - Daily reporting system
- `sprint_visualizer.py` - Sprint progress visualization

### Interactive Tools
- `review_context.py` - Full CLI review system (8KB)
- `hitl_engine.py` - Human-in-the-loop engine
- `hitl_task_metadata.py` - HITL task metadata management

### Data Processing
- `extract_code.py` - Complete code extraction system (18KB)
- `register_output.py` - Complete output registration (22KB)
- `inject_context.py` - Context injection workflows

### Infrastructure
- `thread_safe_workflow.py` - Complete thread-safe implementation (22KB)
- `scalable_storage.py` - Scalable storage management
- `error_handling.py` - Comprehensive error handling

## Example Usage

```bash
# Execute a specific task
python orchestration/execute_task.py --task BE-01

# Run a complete workflow
python orchestration/execute_workflow.py --workflow sprint-planning

# Generate end-of-day report
python orchestration/end_of_day_report.py --date today

# Interactive context review
python orchestration/review_context.py --task TL-05
```

## Architecture Notes
- These are **full implementations** with complete functionality
- Average file size: 10-50KB (production-ready code)
- Includes CLI interfaces, logging, and progress tracking
- Designed for direct execution and human interaction

## Relationship to src/core/workflows/
The `src/core/workflows/` directory contains the **library interfaces** for these implementations. Use this `orchestration/` directory when you need:
- Command-line execution
- Interactive features
- Full logging and monitoring
- Production deployment

Use `src/core/workflows/` when you need:
- Programmatic API access
- Integration with other systems
- Minimal dependencies
- Library-style imports