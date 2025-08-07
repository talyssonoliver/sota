"""
Unified Vercel Tool with Git Integration and Deploy Hooks support.
Combines the best of both implementations with enhanced Git integration functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from pydantic import BaseModel, ValidationError

from src.infrastructure.utils.common_imports import json, os, requests
from src.infrastructure.tools.core.base_tool import ArtesanatoBaseTool


class VercelCommand(ABC):
    """Base class for Vercel API commands."""
    
    def __init__(self, tool: 'VercelTool'):
        self.tool = tool
    
    @abstractmethod
    def can_handle(self, query: str) -> bool:
        """Check if this command can handle the given query."""
        pass
    
    @abstractmethod
    def execute(self, query: str) -> str:
        """Execute the command and return the result."""
        pass


class ProjectCommand(VercelCommand):
    """Handles project-related operations."""
    
    def can_handle(self, query: str) -> bool:
        query_lower = query.lower()
        return "project" in query_lower or "app" in query_lower
    
    def execute(self, query: str) -> str:
        query_lower = query.lower()
        
        if "create project" in query_lower:
            name = self.tool._extract_param(query, "name")
            framework = self.tool._extract_param(query, "framework") or "nextjs"
            git_repo = self.tool._extract_param(query, "git_repo")
            return self.tool._create_project(name, framework, git_repo)
        elif "list projects" in query_lower:
            return self.tool._list_projects()
        elif "delete project" in query_lower:
            project_id = self.tool._extract_param(query, "id") or self.tool.project_id
            return self.tool._delete_project(project_id)
        else:
            project_id = self.tool._extract_param(query, "id") or self.tool.project_id
            return self.tool._get_project(project_id)


class DeploymentCommand(VercelCommand):
    """Handles deployment-related operations with Git integration support."""
    
    def can_handle(self, query: str) -> bool:
        return "deploy" in query.lower()
    
    def execute(self, query: str) -> str:
        query_lower = query.lower()
        
        if "create deployment" in query_lower or "trigger deployment" in query_lower:
            project_id = self.tool._extract_param(query, "project") or self.tool.project_id
            branch = self.tool._extract_param(query, "branch") or "main"
            commit_sha = self.tool._extract_param(query, "commit") or self.tool._extract_param(query, "sha")
            use_hook = "hook" in query_lower or "webhook" in query_lower
            
            if use_hook:
                hook_name = self.tool._extract_param(query, "hook_name") or f"deployment-{branch}"
                return self.tool._trigger_deploy_hook(project_id, hook_name, branch)
            else:
                return self.tool._create_deployment(project_id, branch, commit_sha)
        elif "list deployments" in query_lower:
            project_id = self.tool._extract_param(query, "project") or self.tool.project_id
            return self.tool._list_deployments(project_id)
        else:
            deployment_id = self.tool._extract_param(query, "id")
            return self.tool._get_deployment(deployment_id)


class DeployHookCommand(VercelCommand):
    """Handles Deploy Hook operations - Vercel's Git integration solution."""
    
    def can_handle(self, query: str) -> bool:
        query_lower = query.lower()
        return "hook" in query_lower or "webhook" in query_lower
    
    def execute(self, query: str) -> str:
        query_lower = query.lower()
        project_id = self.tool._extract_param(query, "project") or self.tool.project_id
        
        if "create hook" in query_lower or "add hook" in query_lower:
            name = self.tool._extract_param(query, "name")
            branch = self.tool._extract_param(query, "branch") or "main"
            return self.tool._create_deploy_hook(project_id, name, branch)
        elif "list hooks" in query_lower:
            return self.tool._list_deploy_hooks(project_id)
        elif "delete hook" in query_lower or "remove hook" in query_lower:
            hook_id = self.tool._extract_param(query, "id") or self.tool._extract_param(query, "hook_id")
            return self.tool._delete_deploy_hook(project_id, hook_id)
        elif "trigger hook" in query_lower:
            hook_name = self.tool._extract_param(query, "name")
            branch = self.tool._extract_param(query, "branch") or "main"
            return self.tool._trigger_deploy_hook(project_id, hook_name, branch)
        else:
            hook_id = self.tool._extract_param(query, "id") or self.tool._extract_param(query, "hook_id")
            return self.tool._get_deploy_hook(project_id, hook_id)


class GitIntegrationCommand(VercelCommand):
    """Handles Git repository integration operations."""
    
    def can_handle(self, query: str) -> bool:
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in ["git", "repository", "repo", "github", "gitlab", "bitbucket"])
    
    def execute(self, query: str) -> str:
        query_lower = query.lower()
        project_id = self.tool._extract_param(query, "project") or self.tool.project_id
        
        if "connect git" in query_lower or "link git" in query_lower:
            repo_url = self.tool._extract_param(query, "repo") or self.tool._extract_param(query, "repository")
            branch = self.tool._extract_param(query, "branch") or "main"
            return self.tool._connect_git_repository(project_id, repo_url, branch)
        elif "disconnect git" in query_lower or "unlink git" in query_lower:
            return self.tool._disconnect_git_repository(project_id)
        elif "git status" in query_lower or "repo status" in query_lower:
            return self.tool._get_git_integration_status(project_id)
        else:
            return json.dumps(
                self.tool.format_response(
                    data=None,
                    error="Supported Git operations: connect git, disconnect git, git status"
                )
            )


class DomainCommand(VercelCommand):
    """Handles domain-related operations."""
    
    def can_handle(self, query: str) -> bool:
        return "domain" in query.lower()
    
    def execute(self, query: str) -> str:
        query_lower = query.lower()
        project_id = self.tool._extract_param(query, "project") or self.tool.project_id
        
        if "add domain" in query_lower:
            domain = self.tool._extract_param(query, "name")
            return self.tool._add_domain(project_id, domain)
        elif "list domains" in query_lower:
            return self.tool._list_domains(project_id)
        elif "delete domain" in query_lower or "remove domain" in query_lower:
            domain = self.tool._extract_param(query, "name")
            return self.tool._remove_domain(project_id, domain)
        else:
            domain = self.tool._extract_param(query, "name")
            return self.tool._get_domain(project_id, domain)


class EnvironmentCommand(VercelCommand):
    """Handles environment variable operations."""
    
    def can_handle(self, query: str) -> bool:
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in ["env", "environment", "variable"])
    
    def execute(self, query: str) -> str:
        query_lower = query.lower()
        project_id = self.tool._extract_param(query, "project") or self.tool.project_id
        
        if any(phrase in query_lower for phrase in ["add env", "create env", "set env"]):
            name = (self.tool._extract_param(query, "name") or 
                   self.tool._extract_param(query, "key"))
            value = self.tool._extract_param(query, "value")
            is_secret = "secret" in query_lower
            return self.tool._add_env_variable(project_id, name, value, is_secret)
        elif "list env" in query_lower:
            return self.tool._list_env_variables(project_id)
        elif "delete env" in query_lower or "remove env" in query_lower:
            name = (self.tool._extract_param(query, "name") or 
                   self.tool._extract_param(query, "key"))
            return self.tool._remove_env_variable(project_id, name)
        else:
            name = (self.tool._extract_param(query, "name") or 
                   self.tool._extract_param(query, "key"))
            return self.tool._get_env_variable(project_id, name)


class LogsCommand(VercelCommand):
    """Handles logs operations."""
    
    def can_handle(self, query: str) -> bool:
        return "logs" in query.lower()
    
    def execute(self, query: str) -> str:
        deployment_id = self.tool._extract_param(query, "id")
        return self.tool._get_logs(deployment_id)


class DefaultCommand(VercelCommand):
    """Handles default/fallback operations."""
    
    def can_handle(self, query: str) -> bool:
        return True  # Always can handle as fallback
    
    def execute(self, query: str) -> str:
        query_lower = query.lower()
        
        # Map specific phrases to operations
        operations = {
            "list deployments": lambda: self.tool._list_deployments(),
            "get deployment": lambda: self.tool._get_deployment(
                self.tool._extract_param(query, "id")
            ),
            "list projects": lambda: self.tool._list_projects(),
            "get project": lambda: self.tool._get_project(
                self.tool._extract_param(query, "id") or self.tool.project_id
            ),
            "list env variables": lambda: self.tool._list_env_variables(
                self.tool._extract_param(query, "project") or self.tool.project_id
            ),
            "get logs": lambda: self.tool._get_logs(
                self.tool._extract_param(query, "id")
            ),
        }
        
        for phrase, operation in operations.items():
            if phrase in query_lower:
                return operation()
        
        # No matching operation found
        return json.dumps(
            self.tool.format_response(
                data=None,
                error="Unsupported Vercel operation. Supported operations: "
                      "create/list/get/delete project, create/list/get deployment, "
                      "create/list/delete/trigger deploy hook, connect/disconnect git, "
                      "add/list/get/remove domain, add/list/get/remove env variable, get logs"
            )
        )


class VercelTool(ArtesanatoBaseTool):
    """Unified Vercel Tool with Git Integration and Deploy Hooks support."""

    name: str = "vercel_tool"
    description: str = "Tool for interacting with Vercel deployments, projects, domains, environment variables, and Git integration via Deploy Hooks."
    token: str = os.getenv("VERCEL_TOKEN")
    team_id: str = os.getenv("VERCEL_TEAM_ID", "")
    project_id: str = os.getenv("VERCEL_PROJECT_ID", "")
    project: str = "artesanato-ecommerce"
    api_base_url: str = "https://api.vercel.com"
    headers: Dict[str, str] = {}
    commands: list = []  # Add this as a Pydantic field

    def __init__(self, **kwargs):
        """Initialize the Vercel tool with command handlers."""
        super().__init__(**kwargs)
        
        if self.token:
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        
        # Initialize command handlers after super().__init__()
        # Order matters - more specific commands should come first
        self.commands = [
            DeployHookCommand(self),
            GitIntegrationCommand(self),
            DeploymentCommand(self),
            ProjectCommand(self),
            DomainCommand(self),
            EnvironmentCommand(self),
            LogsCommand(self),
            DefaultCommand(self),  # Must be last as it always returns True for can_handle
        ]

    def _check_env_vars(self) -> None:
        """Check for required environment variables."""
        if not self.token:
            self.log("Warning: VERCEL_TOKEN not found. Vercel API calls will be mocked.")

    class InputSchema(BaseModel):
        query: str

    def _run(self, query: str) -> str:
        """Execute a query against the Vercel API using command pattern."""
        try:
            validated = self.InputSchema(query=query)
            query = validated.query
            
            # Find the first command that can handle this query
            for command in self.commands:
                if command.can_handle(query):
                    return command.execute(query)
            
            # This should never happen since DefaultCommand always returns True
            return json.dumps(
                self.format_response(
                    data=None,
                    error="No command handler found for the query"
                )
            )

        except ValidationError as ve:
            return json.dumps(
                self.handle_error(ve, f"{self.name}._run.input_validation")
            )
        except Exception as e:
            return json.dumps(self.handle_error(e, f"{self.name}._run"))

    def _extract_param(self, query: str, param_name: str) -> Optional[str]:
        """Extract a parameter value from the query string."""
        param_pattern = f"{param_name}:"
        param_start = query.find(param_pattern)
        if param_start == -1:
            return None
        
        param_start += len(param_pattern)
        
        # Find the end of the parameter value
        # Look for space followed by another parameter pattern (word:)
        import re
        remaining = query[param_start:]
        
        # Match until we find a space followed by word: pattern, or end of string
        match = re.match(r'([^\s]+(?:\s+[^:]+)*?)(?:\s+\w+:|$)', remaining)
        if match:
            value = match.group(1).strip()
            return value if value else None
        
        # Fallback: take everything until space or end
        space_pos = remaining.find(' ')
        if space_pos == -1:
            value = remaining.strip()
        else:
            value = remaining[:space_pos].strip()
        
        return value if value else None

    # Enhanced Git Integration Methods

    def _create_deploy_hook(self, project_id: str, name: str, branch: str = "main") -> str:
        """Create a Deploy Hook for Git-triggered deployments."""
        if not self.token or not project_id or not name:
            return self._mock_create_deploy_hook(project_id, name, branch)

        try:
            url = f"{self.api_base_url}/v1/integrations/deploy-hooks"
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id

            payload = {
                "name": name,
                "projectId": project_id,
                "ref": branch
            }

            response = requests.post(
                url, headers=self.headers, params=params, json=payload)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._create_deploy_hook"))

    def _list_deploy_hooks(self, project_id: str) -> str:
        """List Deploy Hooks for a project."""
        if not self.token or not project_id:
            return self._mock_list_deploy_hooks(project_id)

        try:
            url = f"{self.api_base_url}/v1/integrations/deploy-hooks"
            params = {"projectId": project_id}
            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._list_deploy_hooks"))

    def _get_deploy_hook(self, project_id: str, hook_id: str) -> str:
        """Get Deploy Hook details."""
        if not self.token or not project_id or not hook_id:
            return self._mock_get_deploy_hook(project_id, hook_id)

        try:
            url = f"{self.api_base_url}/v1/integrations/deploy-hooks/{hook_id}"
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._get_deploy_hook"))

    def _delete_deploy_hook(self, project_id: str, hook_id: str) -> str:
        """Delete a Deploy Hook."""
        if not self.token or not project_id or not hook_id:
            return self._mock_delete_deploy_hook(project_id, hook_id)

        try:
            url = f"{self.api_base_url}/v1/integrations/deploy-hooks/{hook_id}"
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.delete(url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data={"success": True, "message": f"Deploy Hook {hook_id} deleted successfully"}
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._delete_deploy_hook"))

    def _trigger_deploy_hook(self, project_id: str, hook_name: str, branch: str = "main") -> str:
        """Trigger a Deploy Hook to create a deployment from Git."""
        if not self.token or not project_id or not hook_name:
            return self._mock_trigger_deploy_hook(project_id, hook_name, branch)

        try:
            # First, get the deploy hook URL
            hooks = self._list_deploy_hooks(project_id)
            hooks_data = json.loads(hooks)
            
            hook_url = None
            for hook in hooks_data.get("data", {}).get("hooks", []):
                if hook.get("name") == hook_name:
                    hook_url = hook.get("url")
                    break
            
            if not hook_url:
                return json.dumps(
                    self.format_response(
                        data=None,
                        error=f"Deploy Hook '{hook_name}' not found"
                    )
                )

            # Trigger the deploy hook with a simple POST request
            response = requests.post(hook_url)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data={
                    "success": True,
                    "message": f"Deploy Hook '{hook_name}' triggered successfully",
                    "hook_url": hook_url,
                    "branch": branch
                }
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._trigger_deploy_hook"))

    def _connect_git_repository(self, project_id: str, repo_url: str, branch: str = "main") -> str:
        """Connect a Git repository to a Vercel project."""
        if not self.token or not project_id or not repo_url:
            return self._mock_connect_git_repository(project_id, repo_url, branch)

        try:
            url = f"{self.api_base_url}/v9/projects/{project_id}"
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id

            # Extract repository info from URL
            repo_parts = repo_url.replace("https://github.com/", "").split("/")
            if len(repo_parts) >= 2:
                owner = repo_parts[0]
                repo_name = repo_parts[1].replace(".git", "")
            else:
                return json.dumps(
                    self.format_response(
                        data=None,
                        error="Invalid GitHub repository URL format"
                    )
                )

            payload = {
                "link": {
                    "type": "github",
                    "repo": f"{owner}/{repo_name}",
                    "repoId": None,  # Will be resolved by Vercel
                    "gitSource": {
                        "type": "github",
                        "ref": branch,
                        "sha": None  # Will use latest commit
                    }
                }
            }

            response = requests.patch(
                url, headers=self.headers, params=params, json=payload)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._connect_git_repository"))

    def _disconnect_git_repository(self, project_id: str) -> str:
        """Disconnect Git repository from a Vercel project."""
        if not self.token or not project_id:
            return self._mock_disconnect_git_repository(project_id)

        try:
            url = f"{self.api_base_url}/v9/projects/{project_id}"
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id

            payload = {
                "link": None  # Remove the Git link
            }

            response = requests.patch(
                url, headers=self.headers, params=params, json=payload)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data={
                    "success": True,
                    "message": "Git repository disconnected successfully"
                }
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._disconnect_git_repository"))

    def _get_git_integration_status(self, project_id: str) -> str:
        """Get Git integration status for a project."""
        if not self.token or not project_id:
            return self._mock_get_git_integration_status(project_id)

        try:
            project_data = self._get_project(project_id)
            project_json = json.loads(project_data)
            
            git_integration = project_json.get("data", {}).get("link", {})
            
            if git_integration:
                return json.dumps(self.format_response(
                    data={
                        "connected": True,
                        "provider": git_integration.get("type"),
                        "repository": git_integration.get("repo"),
                        "branch": git_integration.get("gitSource", {}).get("ref"),
                        "integration": git_integration
                    }
                ))
            else:
                return json.dumps(self.format_response(
                    data={
                        "connected": False,
                        "message": "No Git repository connected to this project"
                    }
                ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._get_git_integration_status"))

    # Enhanced deployment creation with Git integration
    def _create_deployment(self, project_id: str, branch: str = "main", commit_sha: Optional[str] = None) -> str:
        """Create a new deployment with enhanced Git integration support."""
        if not self.token or not project_id:
            return self._mock_create_deployment(project_id, branch)

        try:
            url = f"{self.api_base_url}/v13/deployments"
            params = {}

            if self.team_id:
                params["teamId"] = self.team_id

            payload = {
                "name": self.project,
                "projectId": project_id,
                "target": "production" if branch == "main" else "preview",
                "gitSource": {
                    "type": "github",  # Assume GitHub for now, could be made configurable
                    "ref": branch,
                    "sha": commit_sha  # Optional specific commit
                },
                "meta": {
                    "githubBranch": branch
                }
            }

            # Remove None values
            if not commit_sha:
                del payload["gitSource"]["sha"]

            response = requests.post(
                url, headers=self.headers, params=params, json=payload)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._create_deployment"))

    # Copy remaining original methods with minor improvements
    def _create_project(self, name: str, framework: str = "nextjs", git_repo: Optional[str] = None) -> str:
        """Create a new Vercel project with optional Git integration."""
        if not self.token or not name:
            return self._mock_create_project(name, framework)
        try:
            # Idempotency check: see if project already exists
            url = f"{self.api_base_url}/v9/projects/{name}"
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return json.dumps(self.format_response(
                    data=response.json(),
                    error="Project already exists. Returning existing project."
                ))
            
            # If not found, create project
            url = f"{self.api_base_url}/v9/projects"
            payload = {
                "name": name,
                "framework": framework
            }
            
            # Add Git integration if provided
            if git_repo:
                repo_parts = git_repo.replace("https://github.com/", "").split("/")
                if len(repo_parts) >= 2:
                    owner = repo_parts[0]
                    repo_name = repo_parts[1].replace(".git", "")
                    payload["gitRepository"] = {
                        "type": "github",
                        "repo": f"{owner}/{repo_name}"
                    }
            
            response = requests.post(
                url, headers=self.headers, params=params, json=payload)
            response.raise_for_status()
            
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._create_project"))
    
    def _list_projects(self) -> str:
        """List all projects for the configured team or user."""
        if not self.token:
            return self._mock_list_projects()

        try:
            url = f"{self.api_base_url}/v9/projects"
            params = {}

            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._list_projects"))
    
    def _get_project(self, project_id: str) -> str:
        """Get information about a specific project."""
        if not self.token or not project_id:
            return self._mock_get_project(project_id or "artesanato-ecommerce")

        try:
            url = f"{self.api_base_url}/v9/projects/{project_id}"
            params = {}

            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "VercelTool._get_project"))
    
    def _delete_project(self, project_id: str) -> str:
        """Delete a Vercel project."""
        if not self.token or not project_id:
            return self._mock_delete_project(project_id)

        try:
            url = f"{self.api_base_url}/v9/projects/{project_id}"
            params = {}

            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.delete(
                url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data={"success": True,
                      "message": f"Project {project_id} deleted successfully"}
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._delete_project"))
    
    def _list_deployments(self, project_id: str = None) -> str:
        """List recent deployments for the configured project."""
        if not self.token:
            return self._mock_list_deployments()

        try:
            url = f"{self.api_base_url}/v6/deployments"
            params = {}

            if project_id:
                params["projectId"] = project_id
            elif self.project_id:
                params["projectId"] = self.project_id

            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._list_deployments"))

    def _get_deployment(self, deployment_id: str) -> str:
        """Get information about a specific deployment."""
        if not self.token or not deployment_id:
            return self._mock_get_deployment(deployment_id)

        try:
            url = f"{self.api_base_url}/v13/deployments/{deployment_id}"
            params = {}

            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._get_deployment"))

    def _get_logs(self, deployment_id: str) -> str:
        """Get logs for a specific deployment."""
        if not self.token or not deployment_id:
            return self._mock_get_logs(deployment_id or "deployment123")

        try:
            url = f"{self.api_base_url}/v2/deployments/{deployment_id}/events"
            params = {}

            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "VercelTool._get_logs"))

    # Domain operations (unchanged from original)
    def _add_domain(self, project_id: str, domain: str) -> str:
        """Add a domain to a project. Idempotent: will not add duplicate domains."""
        if not self.token or not project_id or not domain:
            return self._mock_add_domain(project_id, domain)
        try:
            # Idempotency check: see if domain already exists for project
            url = f"{self.api_base_url}/v9/projects/{project_id}/domains/{domain}"
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return json.dumps(
                    self.format_response(
                        data=response.json(),
                        error="Domain already exists for this project. Returning existing domain."))
            # If not found, add domain
            url = f"{self.api_base_url}/v9/projects/{project_id}/domains"
            payload = {
                "name": domain
            }
            response = requests.post(
                url, headers=self.headers, params=params, json=payload)
            response.raise_for_status()
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "VercelTool._add_domain"))

    def _list_domains(self, project_id: str) -> str:
        """List domains for a project."""
        if not self.token or not project_id:
            return self._mock_list_domains(project_id)

        try:
            url = f"{self.api_base_url}/v9/projects/{project_id}/domains"
            params = {}

            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "VercelTool._list_domains"))

    def _get_domain(self, project_id: str, domain: str) -> str:
        """Get information about a specific domain."""
        if not self.token or not project_id or not domain:
            return self._mock_get_domain(project_id, domain)

        try:
            url = f"{self.api_base_url}/v9/projects/{project_id}/domains/{domain}"
            params = {}

            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "VercelTool._get_domain"))

    def _remove_domain(self, project_id: str, domain: str) -> str:
        """Remove a domain from a project."""
        if not self.token or not project_id or not domain:
            return self._mock_remove_domain(project_id, domain)

        try:
            url = f"{self.api_base_url}/v9/projects/{project_id}/domains/{domain}"
            params = {}

            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.delete(
                url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data={"success": True,
                      "message": f"Domain {domain} removed successfully"}
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._remove_domain"))

    # Environment variable operations (unchanged from original)
    def _list_env_variables(self, project_id: str) -> str:
        """List environment variables for a project."""
        if not self.token or not project_id:
            return self._mock_list_env_variables(
                project_id or "artesanato-ecommerce")

        try:
            url = f"{self.api_base_url}/v9/projects/{project_id}/env"
            params = {}

            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._list_env_variables"))

    def _add_env_variable(
            self,
            project_id: str,
            name: str,
            value: str,
            is_secret: bool = False) -> str:
        """Add an environment variable to a project. Idempotent: will not add duplicate env variables with the same key."""
        if not self.token or not project_id or not name or not value:
            return self._mock_add_env_variable(
                project_id or "artesanato-ecommerce", name, value, is_secret)
        try:
            # Idempotency check: see if env variable already exists
            url = f"{self.api_base_url}/v9/projects/{project_id}/env"
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            envs = response.json().get("envs", [])
            for env in envs:
                if env.get("key") == name:
                    return json.dumps(
                        self.format_response(
                            data=env,
                            error="Environment variable already exists. Returning existing variable."))
            # If not found, add env variable
            payload = {
                "key": name,
                "value": value,
                "type": "secret" if is_secret else "plain",
                "target": ["production", "preview", "development"]
            }
            response = requests.post(
                url, headers=self.headers, params=params, json=payload)
            response.raise_for_status()
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._add_env_variable"))

    def _get_env_variable(self, project_id: str, name: str) -> str:
        """Get information about a specific environment variable."""
        if not self.token or not project_id or not name:
            return self._mock_get_env_variable(project_id, name)

        try:
            # Note: Vercel API doesn't have a direct endpoint to get a single env var
            # So we list all and filter
            url = f"{self.api_base_url}/v9/projects/{project_id}/env"
            params = {}

            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            envs = response.json()
            target_env = None

            for env in envs.get("envs", []):
                if env.get("key") == name:
                    target_env = env
                    break

            if not target_env:
                return json.dumps(self.format_response(
                    data=None,
                    error=f"Environment variable '{name}' not found"
                ))

            return json.dumps(self.format_response(
                data=target_env
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._get_env_variable"))

    def _remove_env_variable(self, project_id: str, name: str) -> str:
        """Remove an environment variable from a project."""
        if not self.token or not project_id or not name:
            return self._mock_remove_env_variable(project_id, name)

        try:
            # First we need to get the environment variable ID
            url = f"{self.api_base_url}/v9/projects/{project_id}/env"
            params = {}

            if self.team_id:
                params["teamId"] = self.team_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            env_id = None
            for env in response.json().get("envs", []):
                if env.get("key") == name:
                    env_id = env.get("id")
                    break

            if not env_id:
                return json.dumps(self.format_response(
                    data=None,
                    error=f"Environment variable '{name}' not found"
                ))

            # Now delete the environment variable
            url = f"{self.api_base_url}/v9/projects/{project_id}/env/{env_id}"
            response = requests.delete(
                url, headers=self.headers, params=params)
            response.raise_for_status()

            return json.dumps(
                self.format_response(
                    data={
                        "success": True,
                        "message": f"Environment variable '{name}' removed successfully"}))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "VercelTool._remove_env_variable"))

    # Enhanced Mock Methods for Testing and Development
    def _mock_create_deploy_hook(self, project_id: str, name: str, branch: str) -> str:
        """Mock response for creating a deploy hook."""
        from datetime import datetime
        return json.dumps(self.format_response(
            data={
                "id": "hook_abc123def456",
                "name": name,
                "url": f"https://api.vercel.com/v1/integrations/deploy-hooks/hook_abc123def456/{project_id}",
                "projectId": project_id,
                "ref": branch,
                "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        ))

    def _mock_list_deploy_hooks(self, project_id: str) -> str:
        """Mock response for listing deploy hooks."""
        from datetime import datetime
        return json.dumps(self.format_response(
            data={
                "hooks": [
                    {
                        "id": "hook_abc123def456",
                        "name": "deployment-main",
                        "url": f"https://api.vercel.com/v1/integrations/deploy-hooks/hook_abc123def456/{project_id}",
                        "projectId": project_id,
                        "ref": "main",
                        "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    },
                    {
                        "id": "hook_def456ghi789",
                        "name": "deployment-develop",
                        "url": f"https://api.vercel.com/v1/integrations/deploy-hooks/hook_def456ghi789/{project_id}",
                        "projectId": project_id,
                        "ref": "develop",
                        "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    }
                ]
            }
        ))

    def _mock_get_deploy_hook(self, project_id: str, hook_id: str) -> str:
        """Mock response for getting a deploy hook."""
        from datetime import datetime
        return json.dumps(self.format_response(
            data={
                "id": hook_id,
                "name": "deployment-main",
                "url": f"https://api.vercel.com/v1/integrations/deploy-hooks/{hook_id}/{project_id}",
                "projectId": project_id,
                "ref": "main",
                "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        ))

    def _mock_delete_deploy_hook(self, project_id: str, hook_id: str) -> str:
        """Mock response for deleting a deploy hook."""
        return json.dumps(self.format_response(
            data={
                "success": True,
                "message": f"Deploy Hook {hook_id} deleted successfully"
            }
        ))

    def _mock_trigger_deploy_hook(self, project_id: str, hook_name: str, branch: str) -> str:
        """Mock response for triggering a deploy hook."""
        return json.dumps(self.format_response(
            data={
                "success": True,
                "message": f"Deploy Hook '{hook_name}' triggered successfully",
                "hook_url": f"https://api.vercel.com/v1/integrations/deploy-hooks/hook_abc123def456/{project_id}",
                "branch": branch,
                "deployment": {
                    "id": "dpl_123abc456def",
                    "url": f"artesanato-ecommerce-git-{branch}.vercel.app",
                    "state": "BUILDING"
                }
            }
        ))

    def _mock_connect_git_repository(self, project_id: str, repo_url: str, branch: str) -> str:
        """Mock response for connecting a Git repository."""
        from datetime import datetime
        return json.dumps(self.format_response(
            data={
                "success": True,
                "message": f"Git repository {repo_url} connected successfully",
                "project": {
                    "id": project_id,
                    "link": {
                        "type": "github",
                        "repo": repo_url.replace("https://github.com/", ""),
                        "gitSource": {
                            "type": "github",
                            "ref": branch,
                            "sha": "abc123def456789"
                        }
                    },
                    "updatedAt": datetime.now().isoformat() + "Z"
                }
            }
        ))

    def _mock_disconnect_git_repository(self, project_id: str) -> str:
        """Mock response for disconnecting a Git repository."""
        return json.dumps(self.format_response(
            data={
                "success": True,
                "message": "Git repository disconnected successfully"
            }
        ))

    def _mock_get_git_integration_status(self, project_id: str) -> str:
        """Mock response for getting Git integration status."""
        return json.dumps(self.format_response(
            data={
                "connected": True,
                "provider": "github",
                "repository": "user/artesanato-ecommerce",
                "branch": "main",
                "integration": {
                    "type": "github",
                    "repo": "user/artesanato-ecommerce",
                    "gitSource": {
                        "type": "github",
                        "ref": "main",
                        "sha": "abc123def456789"
                    }
                }
            }
        ))

    # Original mock methods (unchanged)
    def _mock_create_project(self, name: str, framework: str) -> str:
        """Return mock response for project creation."""
        from datetime import datetime
        project_name = name or "artesanato-ecommerce"
        return json.dumps(self.format_response(
            data={
                "id": "prj_abc123def456",
                "name": project_name,
                "framework": framework,
                "rootDirectory": None,
                "buildCommand": None,
                "devCommand": None,
                "installCommand": None,
                "outputDirectory": None,
                "publicSource": False,
                "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        ))

    def _mock_list_projects(self) -> str:
        """Return mock list of projects."""
        from datetime import datetime, timedelta
        return json.dumps(
            self.format_response(
                data={
                    "projects": [
                        {
                            "id": "prj_abc123def456",
                            "name": "artesanato-ecommerce",
                            "framework": "nextjs",
                            "created": (datetime.now() - timedelta(days=30)).isoformat() + "Z"
                        },
                        {
                            "id": "prj_def456ghi789",
                            "name": "artesanato-admin",
                            "framework": "nextjs",
                            "created": (datetime.now() - timedelta(days=15)).isoformat() + "Z"
                        }
                    ]
                }
            )
        )
    def _mock_get_project(self, project_id: str) -> str:
        """Return mock project information."""
        from datetime import datetime, timedelta
        return json.dumps(
            self.format_response(
                data={
                    "id": project_id,
                    "name": "artesanato-ecommerce",
                    "framework": "nextjs",
                    "rootDirectory": None,
                    "buildCommand": None,
                    "devCommand": None,
                    "installCommand": None,
                    "outputDirectory": None,
                    "publicSource": False,
                    "created": (datetime.now() - timedelta(days=30)).isoformat() + "Z",
                    "updatedAt": datetime.now().isoformat() + "Z",
                    "latestDeployments": [
                        {
                            "id": "dpl_123abc456def",
                            "url": "artesanato-ecommerce-git-main.vercel.app",
                            "created": (datetime.now() - timedelta(days=1)).isoformat() + "Z",
                            "state": "READY"
                        }
                    ],
                    "link": {
                        "type": "github",
                        "repo": "user/artesanato-ecommerce",
                        "gitSource": {
                            "type": "github",
                            "ref": "main",
                            "sha": "abc123def456789"
                        }
                    }
                }
            )
        )

    def _mock_delete_project(self, project_id: str) -> str:
        """Return mock response for project deletion."""
        return json.dumps(self.format_response(
            data={
                "success": True,
                "message": "Project deleted successfully"
            }
        ))

    def _mock_create_deployment(self, project_id: str, branch: str) -> str:
        """Return mock response for deployment creation."""
        from datetime import datetime
        return json.dumps(self.format_response(
            data={
                "id": "dpl_123abc456def",
                "url": f"artesanato-ecommerce-git-{branch}.vercel.app",
                "name": "artesanato-ecommerce",
                "project": project_id,
                "meta": {
                    "githubCommitSha": "abcdef123456789",
                    "githubCommitAuthor": "Developer",
                    "githubCommitMessage": "Implement new features"
                },
                "target": "production" if branch == "main" else "preview",
                "state": "READY",
                "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        ))

    def _mock_list_deployments(self) -> str:
        """Return mock list of deployments."""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        yesterday = datetime.now().replace(day=datetime.now().day -
                                           1).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return json.dumps(self.format_response(
            data={
                "deployments": [
                    {
                        "uid": "dpl_123abc456def",
                        "name": "artesanato-ecommerce",
                        "url": "artesanato-ecommerce-git-main.vercel.app",
                        "created": now,
                        "state": "READY",
                        "target": "production",
                        "meta": {
                            "githubCommitMessage": "Add product filtering functionality"
                        }
                    },
                    {
                        "uid": "dpl_456def789ghi",
                        "name": "artesanato-ecommerce",
                        "url": "artesanato-ecommerce-git-feature-auth.vercel.app",
                        "created": yesterday,
                        "state": "READY",
                        "target": "preview",
                        "meta": {
                            "githubCommitMessage": "Add user authentication"
                        }
                    }
                ]
            }
        ))

    def _mock_get_deployment(self, deployment_id: str) -> str:
        """Return mock deployment information."""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return json.dumps(
            self.format_response(
                data={
                    "id": deployment_id or "dpl_123abc456def",
                    "url": "artesanato-ecommerce-git-main.vercel.app",
                    "name": "artesanato-ecommerce",
                    "project": "prj_abc123def456",
                    "meta": {
                        "githubCommitSha": "abcdef123456789",
                        "githubCommitAuthor": "Developer",
                        "githubCommitMessage": "Add product filtering functionality"},
                    "target": "production",
                    "state": "READY",
                    "created": now,
                    "ready": datetime.now().replace(
                        minute=datetime.now().minute +
                        2).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}))

    def _mock_add_domain(self, project_id: str, domain: str) -> str:
        """Return mock response for adding a domain."""
        from datetime import datetime
        domain_name = domain or "artesanato-ecommerce.com"
        return json.dumps(self.format_response(
            data={
                "name": domain_name,
                "projectId": project_id,
                "verified": True,
                "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        ))

    def _mock_list_domains(self, project_id: str) -> str:
        """Return mock list of domains."""
        from datetime import datetime
        return json.dumps(
            self.format_response(
                data={
                    "domains": [
                        {
                            "name": "artesanato-ecommerce.com",
                            "projectId": project_id,
                            "verified": True,
                            "created": datetime.now().replace(
                                day=datetime.now().day -
                                5).strftime("%Y-%m-%dT%H:%M:%S.%fZ")},
                        {
                            "name": "www.artesanato-ecommerce.com",
                            "projectId": project_id,
                            "verified": True,
                            "created": datetime.now().replace(
                                day=datetime.now().day -
                                5).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}]}))

    def _mock_get_domain(self, project_id: str, domain: str) -> str:
        """Return mock domain information."""
        from datetime import datetime
        domain_name = domain or "artesanato-ecommerce.com"
        return json.dumps(
            self.format_response(
                data={
                    "name": domain_name,
                    "projectId": project_id,
                    "verified": True,
                    "created": datetime.now().replace(
                        day=datetime.now().day -
                        5).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "updatedAt": datetime.now().replace(
                        day=datetime.now().day -
                        5).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}))

    def _mock_remove_domain(self, project_id: str, domain: str) -> str:
        """Return mock response for removing a domain."""
        return json.dumps(self.format_response(
            data={
                "success": True,
                "message": f"Domain {domain} removed successfully"
            }
        ))

    def _mock_list_env_variables(self, project_id: str) -> str:
        """Return mock list of environment variables."""
        return json.dumps(self.format_response(
            data={
                "envs": [
                    {
                        "id": "env_abc123def456",
                        "key": "NEXT_PUBLIC_SUPABASE_URL",
                        "value": "[REDACTED]",
                        "type": "plain",
                        "target": ["production", "preview", "development"],
                        "gitBranch": ""
                    },
                    {
                        "id": "env_def456ghi789",
                        "key": "NEXT_PUBLIC_SUPABASE_ANON_KEY",
                        "value": "[REDACTED]",
                        "type": "secret",
                        "target": ["production", "preview", "development"],
                        "gitBranch": ""
                    },
                    {
                        "id": "env_ghi789jkl012",
                        "key": "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY",
                        "value": "[REDACTED]",
                        "type": "secret",
                        "target": ["production", "preview", "development"],
                        "gitBranch": ""
                    }
                ]
            }
        ))

    def _mock_add_env_variable(
            self,
            project_id: str,
            name: str,
            value: str,
            is_secret: bool) -> str:
        """Return mock response for adding an environment variable."""
        from datetime import datetime
        return json.dumps(self.format_response(
            data={
                "id": "env_abc123def456",
                "key": name,
                "value": "[REDACTED]" if is_secret else value,
                "type": "secret" if is_secret else "plain",
                "target": ["production", "preview", "development"],
                "projectId": project_id,
                "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        ))

    def _mock_get_env_variable(self, project_id: str, name: str) -> str:
        """Return mock response for getting an environment variable."""
        from datetime import datetime
        return json.dumps(
            self.format_response(
                data={
                    "id": "env_abc123def456",
                    "key": name or "NEXT_PUBLIC_SUPABASE_URL",
                    "value": "[REDACTED]",
                    "type": "plain",
                    "target": [
                        "production",
                        "preview",
                        "development"],
                    "projectId": project_id,
                    "created": datetime.now().replace(
                        day=datetime.now().day -
                        10).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "updatedAt": datetime.now().replace(
                        day=datetime.now().day -
                        10).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}))

    def _mock_remove_env_variable(self, project_id: str, name: str) -> str:
        """Return mock response for removing an environment variable."""
        return json.dumps(self.format_response(
            data={
                "success": True,
                "message": f"Environment variable '{name}' removed successfully"
            }
        ))

    def _mock_get_logs(self, deployment_id: str) -> str:
        """Return mock deployment logs."""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        one_min_ago = datetime.now().replace(
            minute=datetime.now().minute -
            1).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return json.dumps(self.format_response(
            data={
                "logs": [
                    {
                        "type": "stdout",
                        "created": one_min_ago,
                        "message": "Installing dependencies..."
                    },
                    {
                        "type": "stdout",
                        "created": now,
                        "message": "Build completed successfully"
                    }
                ]
            }
        ))
