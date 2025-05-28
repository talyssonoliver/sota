"""
Vercel Tool - Allows agents to interact with Vercel deployments
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel, ValidationError

from tools.base_tool import ArtesanatoBaseTool


class VercelTool(ArtesanatoBaseTool):
    """Tool for interacting with Vercel deployments and configurations."""

    name: str = "vercel_tool"
    description: str = "Tool for interacting with Vercel deployments, projects, domains, and environment variables."
    token: str = os.getenv("VERCEL_TOKEN")
    team_id: str = os.getenv("VERCEL_TEAM_ID", "")
    project_id: str = os.getenv("VERCEL_PROJECT_ID", "")
    project: str = "artesanato-ecommerce"
    api_base_url: str = "https://api.vercel.com"
    headers: Dict[str, str] = {}  # Define headers as a class attribute

    def __init__(self, **kwargs):
        """Initialize the Vercel tool."""
        super().__init__(**kwargs)

        # Check if token exists before attempting to raise an error
        if self.token:
            # Set up headers for API requests
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }

    def _check_env_vars(self) -> None:
        """Check for required environment variables."""
        if not self.token:
            self.log(
                "Warning: VERCEL_TOKEN not found. Vercel API calls will be mocked.")

    class InputSchema(BaseModel):
        query: str

    def _run(self, query: str) -> str:
        """Execute a query against the Vercel API."""
        try:
            validated = self.InputSchema(query=query)
            query = validated.query
            query_lower = query.lower()

            # Project operations
            if "project" in query_lower or "app" in query_lower:
                if "create project" in query_lower:
                    name = self._extract_param(query, "name")
                    framework = self._extract_param(
                        query, "framework") or "nextjs"
                    return self._create_project(name, framework)
                elif "list projects" in query_lower:
                    return self._list_projects()
                elif "delete project" in query_lower:
                    project_id = self._extract_param(
                        query, "id") or self.project_id
                    return self._delete_project(project_id)
                else:
                    project_id = self._extract_param(
                        query, "id") or self.project_id
                    return self._get_project(project_id)

            # Deployment operations
            elif "deploy" in query_lower:
                if "create deployment" in query_lower or "trigger deployment" in query_lower:
                    project_id = self._extract_param(
                        query, "project") or self.project_id
                    branch = self._extract_param(query, "branch") or "main"
                    return self._create_deployment(project_id, branch)
                elif "list deployments" in query_lower:
                    project_id = self._extract_param(
                        query, "project") or self.project_id
                    return self._list_deployments(project_id)
                else:
                    deployment_id = self._extract_param(query, "id")
                    return self._get_deployment(deployment_id)

            # Domain operations
            elif "domain" in query_lower:
                if "add domain" in query_lower:
                    project_id = self._extract_param(
                        query, "project") or self.project_id
                    domain = self._extract_param(query, "name")
                    return self._add_domain(project_id, domain)
                elif "list domains" in query_lower:
                    project_id = self._extract_param(
                        query, "project") or self.project_id
                    return self._list_domains(project_id)
                elif "delete domain" in query_lower or "remove domain" in query_lower:
                    project_id = self._extract_param(
                        query, "project") or self.project_id
                    domain = self._extract_param(query, "name")
                    return self._remove_domain(project_id, domain)
                else:
                    project_id = self._extract_param(
                        query, "project") or self.project_id
                    domain = self._extract_param(query, "name")
                    return self._get_domain(project_id, domain)

            # Environment variable operations
            elif "env" in query_lower or "environment" in query_lower or "variable" in query_lower:
                if "add env" in query_lower or "create env" in query_lower or "set env" in query_lower:
                    project_id = self._extract_param(
                        query, "project") or self.project_id
                    name = self._extract_param(
                        query, "name") or self._extract_param(query, "key")
                    value = self._extract_param(query, "value")
                    is_secret = "secret" in query_lower
                    return self._add_env_variable(
                        project_id, name, value, is_secret)
                elif "list env" in query_lower:
                    project_id = self._extract_param(
                        query, "project") or self.project_id
                    return self._list_env_variables(project_id)
                elif "delete env" in query_lower or "remove env" in query_lower:
                    project_id = self._extract_param(
                        query, "project") or self.project_id
                    name = self._extract_param(
                        query, "name") or self._extract_param(query, "key")
                    return self._remove_env_variable(project_id, name)
                else:
                    project_id = self._extract_param(
                        query, "project") or self.project_id
                    name = self._extract_param(
                        query, "name") or self._extract_param(query, "key")
                    return self._get_env_variable(project_id, name)

            # Log operations
            elif "logs" in query_lower:
                deployment_id = self._extract_param(query, "id")
                return self._get_logs(deployment_id)

            # Default operations based on keywords
            elif "list deployments" in query_lower:
                return self._list_deployments()
            elif "get deployment" in query_lower:
                deployment_id = self._extract_param(query, "id")
                return self._get_deployment(deployment_id)
            elif "list projects" in query_lower:
                return self._list_projects()
            elif "get project" in query_lower:
                project_id = self._extract_param(
                    query, "id") or self.project_id
                return self._get_project(project_id)
            elif "list env variables" in query_lower:
                project_id = self._extract_param(
                    query, "project") or self.project_id
                return self._list_env_variables(project_id)
            elif "get logs" in query_lower:
                deployment_id = self._extract_param(query, "id")
                return self._get_logs(deployment_id)
            else:
                return json.dumps(
                    self.format_response(
                        data=None,
                        error="Unsupported Vercel operation. Supported operations: create/list/get/delete project, create/list/get deployment, add/list/get/remove domain, add/list/get/remove env variable, get logs"))

        except ValidationError as ve:
            return json.dumps(
                self.handle_error(
                    ve, f"{
                        self.name}._run.input_validation"))
        except Exception as e:
            return json.dumps(self.handle_error(e, f"{self.name}._run"))

    def _extract_param(self, query: str, param_name: str) -> str:
        """Extract a parameter value from the query string."""
        param_start = query.find(f"{param_name}:") + len(param_name) + 1
        if (param_start < len(param_name) + 1):
            return ""

        # Find the end of the parameter value
        next_param_pos = query[param_start:].find(":")
        param_end = param_start + \
            next_param_pos if next_param_pos != -1 else len(query)

        # If there's a comma before the next param, use that as the end
        comma_pos = query[param_start:].find(",")
        if comma_pos != - \
                1 and (comma_pos < next_param_pos or next_param_pos == -1):
            param_end = param_start + comma_pos

        return query[param_start:param_end].strip()

    # Project operations

    def _create_project(self, name: str, framework: str = "nextjs") -> str:
        """Create a new Vercel project. Idempotent: will not create duplicate projects with the same name."""
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

    # Deployment operations

    def _create_deployment(self, project_id: str, branch: str = "main") -> str:
        """Create a new deployment for a project."""
        if not self.token or not project_id:
            return self._mock_create_deployment(project_id, branch)

        try:
            # Note: Triggering deployments through the API usually requires a Git integration
            # This is a simplified version for demonstration
            url = f"{self.api_base_url}/v13/deployments"
            params = {}

            if self.team_id:
                params["teamId"] = self.team_id

            payload = {
                "name": self.project,
                "projectId": project_id,
                "target": "production" if branch == "main" else "preview",
                "meta": {
                    "githubBranch": branch
                }
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
                    e, "VercelTool._create_deployment"))

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

    # Domain operations

    def _add_domain(self, project_id: str, domain: str) -> str:
        """Add a domain to a project. Idempotent: will not add duplicate domains."""
        if not self.token or not project_id or not domain:
            return self._mock_add_domain(project_id, domain)
        try:
            # Idempotency check: see if domain already exists for project
            url = f"{
                self.api_base_url}/v9/projects/{project_id}/domains/{domain}"
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
            url = f"{
                self.api_base_url}/v9/projects/{project_id}/domains/{domain}"
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
            url = f"{
                self.api_base_url}/v9/projects/{project_id}/domains/{domain}"
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

    # Environment variable operations

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

    # Mock responses for when Vercel token is unavailable
    def _mock_create_project(self, name: str, framework: str) -> str:
        """Return mock response for project creation."""
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
        return json.dumps(
            self.format_response(
                data={
                    "projects": [
                        {
                            "id": "prj_abc123def456",
                            "name": "artesanato-ecommerce",
                            "framework": "nextjs",
                            "created": datetime.now().replace(
                                day=datetime.now().day -
                                30).strftime("%Y-%m-%dT%H:%M:%S.%fZ")},
                        {
                            "id": "prj_def456ghi789",
                            "name": "artesanato-admin",
                            "framework": "nextjs",
                            "created": datetime.now().replace(
                                day=datetime.now().day -
                                15).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}]}))

    def _mock_get_project(self, project_id: str) -> str:
        """Return mock project information."""
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
                    "created": datetime.now().replace(
                        day=datetime.now().day -
                        30).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "latestDeployments": [
                        {
                            "id": "dpl_123abc456def",
                            "url": "artesanato-ecommerce-git-main.vercel.app",
                            "created": datetime.now().replace(
                                day=datetime.now().day -
                                1).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                            "state": "READY"}]}))

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
