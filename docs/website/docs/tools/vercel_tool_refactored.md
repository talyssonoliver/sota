# tools/vercel_tool_refactored.py

## Classes
- **VercelCommand** (line 18)
  - Methods: __init__, can_handle, execute
- **ProjectCommand** (line 35)
  - Methods: can_handle, execute
- **DeploymentCommand** (line 59)
  - Methods: can_handle, execute
- **DomainCommand** (line 80)
  - Methods: can_handle, execute
- **EnvironmentCommand** (line 103)
  - Methods: can_handle, execute
- **LogsCommand** (line 132)
  - Methods: can_handle, execute
- **DefaultCommand** (line 143)
  - Methods: can_handle, execute
- **VercelToolRefactored** (line 185)
  - Methods: __init__, _check_env_vars, _run, _extract_param, _create_project, _list_projects, _get_project, _delete_project, _create_deployment, _list_deployments, _get_deployment, _add_domain, _list_domains, _get_domain, _remove_domain, _add_env_variable, _list_env_variables, _get_env_variable, _remove_env_variable, _get_logs
