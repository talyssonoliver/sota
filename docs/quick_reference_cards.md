# Quick Reference Cards

## Agent Quick Reference
| Agent | Primary Tools | Key Responsibilities |
|-------|---------------|---------------------|
| TechLead | memory_engine, task_analyzer | Architecture, planning |
| Backend | code_generator, db_tools | API implementation |
| Frontend | code_generator, design_system_tool | UI implementation |
| QA | coverage_tool, cypress_tool | Testing and validation |
| Documentation | markdown_tool, context_tracker | Documentation generation |
| Coordinator | tool_loader, memory_engine | Multi-agent orchestration |

## Task State Quick Reference
| State | Next States | Trigger |
|-------|------------|---------|
| CREATED | QUEUED | Orchestrator queues |
| QUEUED | ASSIGNED | Agent available |
| ASSIGNED | IN_PROGRESS | Agent starts task |
| IN_PROGRESS | BLOCKED, REVIEW, COMPLETED | Dependency issues or completion |
| BLOCKED | IN_PROGRESS | Dependency resolved |
| REVIEW | COMPLETED, IN_PROGRESS | Approval or revisions |
| COMPLETED | - | Task done |
| FAILED | - | Error encountered |
| CANCELLED | - | Manually cancelled |

## Common Commands
```bash
# Run workflow
python main.py --workflow [name]

# Test tools
python main.py --test-tools

# View logs
tail -f logs/orchestrator.log
```
