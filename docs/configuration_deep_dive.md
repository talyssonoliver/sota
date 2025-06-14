# Configuration Deep Dive

This guide expands on the basic configuration reference by explaining how configuration values are resolved and provides usage examples.

## Environment Variable Precedence

1. **Command Line / Runtime** – values exported directly in the shell take precedence.
2. **`.env` File** – if present, variables defined here fill in missing values.
3. **Default Values** – many tools define sensible defaults when a variable is absent.

Environment variables are loaded early in `main.py` using `dotenv` so that agents and tools all see consistent configuration.

## Configuration Files

- `config/agents.yaml` – defines each agent role, its prompts, and tool assignments.
- `config/tools.yaml` – mapping of tool names to Python classes and required variables.
- `config/daily_cycle.json` – schedules the daily automation run and email settings.
- `config/hitl_policies.yaml` – policies for human‑in‑the‑loop approvals.

Configuration files are loaded through helper functions in `utils/task_loader.py` or directly within the orchestration scripts.

## Example Usage

```bash
export OPENAI_API_KEY=sk-...
python main.py --cycle daily
```

```python
from utils.task_loader import load_task_metadata
meta = load_task_metadata("BE-07")
print(meta["state"])
```

This layered approach keeps configuration flexible across development and production environments.
