# orchestration/task_declaration.py

## Classes
- **TaskPreparationStatus** (line 38)
- **TaskDeclaration** (line 48)
  - Methods: to_dict, from_metadata, from_dict
- **TaskDeclarationManager** (line 133)
  - Methods: __init__, declare_task, prepare_task_for_execution, _validate_task_metadata, _load_task_context, _generate_task_prompt, _get_prompt_template, _validate_dependencies, _create_execution_plan, _get_expected_transitions, _save_declaration_metadata, _load_existing_declarations, get_tasks_ready_for_execution, get_task_declaration, declare_all_tasks, prepare_all_tasks, get_preparation_summary

## Functions
- **main()** (line 656)
