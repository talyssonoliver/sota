import os

"""
test_update_task_status.py - Optimized Test Structure

Migrated from: tests/workflows	est_update_task_status.py
New location: tests/unit\\core	asks	est_update_task_status.py

Part of the optimized test pyramid reorganization:
- Tests now mirror src/ structure
- Proper categorization (unit/integration/e2e)
- Improved mocking and isolation
"""
'\nTest for Step 4.7 — Update Task Status\nValidates that the update_task_state function sets the correct state in the YAML file.\n'
import os as _os
import yaml
from src.infrastructure.utils.task_loader import load_task_metadata, update_task_state
try:
    pass
except ImportError:
    pass
    pass

def test_update_task_status_sets_done(tmp_path):
    task_id = 'TEST-07'
    tasks_dir = tmp_path / 'tasks'
    tasks_dir.mkdir(exist_ok=True)
    task_file = tasks_dir / f'{task_id}.yaml'
    initial_data = {'id': task_id, 'title': 'Test Task', 'state': 'IN_PROGRESS'}
    with open(task_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(initial_data, f)
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        update_task_state(task_id, 'DONE')
        updated = load_task_metadata(task_id)
        assert updated['state'] == 'DONE'
    finally:
        os.chdir(orig_cwd)