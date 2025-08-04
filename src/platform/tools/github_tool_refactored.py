
from src.infrastructure.utils.common_imports import (
    Dict,
    List,
    os,
    requests
)
"""
GitHub Tool - Refactored to use BaseAPITool
Demonstrates clean architecture with base classes and reduced duplication.
"""

# import os  # Consolidated to common_imports
# from typing import Dict, List  # Consolidated to common_imports

# import requests  # Consolidated to common_imports
from pydantic import BaseModel, ValidationError

from src.infrastructure.utils.base_classes import BaseAPITool


class GitHubTool(BaseAPITool):
    """Tool for interacting with GitHub repositories using clean architecture patterns."""

    def __init__(self, **kwargs):
        """Initialize GitHub tool with BaseAPITool benefits."""
        super().__init__(name="github_tool", **kwargs)
        
        # Set GitHub-specific defaults
        self.repo = kwargs.get("repo", self.config.get("repo", "artesanato-shop/artesanato-ecommerce"))

    def _get_default_config(self) -> Dict[str, str]:
        """GitHub-specific default configuration."""
        config = super()._get_default_config()
        config.update({
            "base_url": "https://api.github.com",
            "repo": "artesanato-shop/artesanato-ecommerce",
            "timeout": 30
        })
        return config

    def _load_credentials(self):
        """Load GitHub-specific credentials."""
        super()._load_credentials()
        
        # GitHub uses different token names
        if not self.token:
            github_token_vars = ["GITHUB_TOKEN", "GH_TOKEN"]
            for var in github_token_vars:
                self.token = self.config.get(var.lower()) or os.getenv(var)
                if self.token:
                    break

    def _get_required_fields(self) -> List[str]:
        """GitHub requires token for API access."""
        return ["token"] if not self.config.get("test_mode") else []

    def _get_headers(self) -> Dict[str, str]:
        """Get GitHub-specific API headers."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        return headers

    class InputSchema(BaseModel):
        """Validation schema for GitHub queries."""
        query: str

    def _execute(self, query: str) -> Dict[str, any]:
        """Execute GitHub API operations with validation."""
        try:
            validated = self.InputSchema(query=query)
            query = validated.query.lower()
            
            # Route to appropriate handler
            if "issue" in query:
                return self._handle_issues(query)
            elif "pull request" in query or "pr" in query:
                return self._handle_pull_requests(query)
            elif "repo" in query or "repository" in query:
                return self._handle_repositories(query)
            elif "branch" in query:
                return self._handle_branches(query)
            elif "commit" in query:
                return self._handle_commits(query)
            else:
                return self._format_error_response(
                    "Unsupported GitHub operation. Supported: issues, pull requests, repositories, branches, commits"
                )

        except ValidationError as e:
            return self._format_error_response(f"Invalid input: {e}")

    def _handle_issues(self, query: str) -> Dict[str, any]:
        """Handle issue-related operations."""
        if "list issues" in query:
            return self._list_issues()
        elif "create issue" in query:
            title = self._extract_param(query, "title")
            body = self._extract_param(query, "body")
            return self._create_issue(title, body)
        elif "get issue" in query:
            number = self._extract_param(query, "number")
            return self._get_issue(number)
        else:
            return self._format_error_response("Unsupported issue operation")

    def _handle_pull_requests(self, query: str) -> Dict[str, any]:
        """Handle pull request operations."""
        if "list" in query:
            return self._list_pull_requests()
        elif "create" in query:
            title = self._extract_param(query, "title")
            body = self._extract_param(query, "body")
            head = self._extract_param(query, "head")
            base = self._extract_param(query, "base") or "main"
            return self._create_pull_request(title, body, head, base)
        else:
            return self._format_error_response("Unsupported pull request operation")

    def _handle_repositories(self, query: str) -> Dict[str, any]:
        """Handle repository operations."""
        if "create" in query:
            name = self._extract_param(query, "name")
            description = self._extract_param(query, "description")
            private = "private" in query
            return self._create_repository(name, description, private)
        else:
            return self._get_repository_info()

    def _handle_branches(self, query: str) -> Dict[str, any]:
        """Handle branch operations."""
        if "list" in query:
            return self._list_branches()
        elif "create" in query:
            name = self._extract_param(query, "name")
            base = self._extract_param(query, "base") or "main"
            return self._create_branch(name, base)
        else:
            name = self._extract_param(query, "name")
            return self._get_branch(name) if name else self._list_branches()

    def _handle_commits(self, query: str) -> Dict[str, any]:
        """Handle commit operations."""
        if "list" in query:
            return self._list_commits()
        else:
            sha = self._extract_param(query, "sha")
            return self._get_commit(sha) if sha else self._list_commits()

    def _extract_param(self, query: str, param_name: str) -> str:
        """Extract parameter from query string."""
        param_marker = f"{param_name}:"
        start = query.find(param_marker)
        if start == -1:
            return ""
        
        start += len(param_marker)
        end = query.find(",", start)
        if end == -1:
            end = len(query)
        
        return query[start:end].strip()

    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, any]:
        """Make authenticated GitHub API request."""
        if not self.token and not self.config.get("test_mode"):
            return self._get_mock_response(endpoint, method)
        
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=self.config.get("timeout", 30))
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=self.config.get("timeout", 30))
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data, timeout=self.config.get("timeout", 30))
            else:
                return self._format_error_response(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return self._format_success_response(response.json())
            
        except requests.RequestException as e:
            return self._format_error_response(f"GitHub API error: {e}")

    def _list_issues(self) -> Dict[str, any]:
        """List open issues in the repository."""
        return self._make_request(f"/repos/{self.repo}/issues")

    def _create_issue(self, title: str, body: str) -> Dict[str, any]:
        """Create a new issue with idempotency check."""
        if not title:
            return self._format_error_response("Title is required for issue creation")
        
        # Check for existing issue with same title
        existing = self._make_request(f"/repos/{self.repo}/issues?state=open")
        if existing.get("status") == "success":
            for issue in existing.get("data", []):
                if issue.get("title") == title:
                    return self._format_success_response(
                        issue, 
                        "Issue already exists with this title"
                    )
        
        # Create new issue
        return self._make_request(
            f"/repos/{self.repo}/issues",
            method="POST",
            data={"title": title, "body": body}
        )

    def _get_issue(self, number: str) -> Dict[str, any]:
        """Get specific issue by number."""
        if not number:
            return self._format_error_response("Issue number is required")
        
        return self._make_request(f"/repos/{self.repo}/issues/{number}")

    def _list_pull_requests(self) -> Dict[str, any]:
        """List open pull requests."""
        return self._make_request(f"/repos/{self.repo}/pulls")

    def _create_pull_request(self, title: str, body: str, head: str, base: str) -> Dict[str, any]:
        """Create pull request with idempotency check."""
        if not all([title, head]):
            return self._format_error_response("Title and head branch are required")
        
        # Check for existing PR
        existing = self._make_request(f"/repos/{self.repo}/pulls?state=open&head={head}&base={base}")
        if existing.get("status") == "success":
            for pr in existing.get("data", []):
                if pr.get("title") == title:
                    return self._format_success_response(
                        pr,
                        "Pull request already exists with this title and branch"
                    )
        
        # Create new PR
        return self._make_request(
            f"/repos/{self.repo}/pulls",
            method="POST",
            data={"title": title, "body": body, "head": head, "base": base}
        )

    def _get_repository_info(self) -> Dict[str, any]:
        """Get repository information."""
        return self._make_request(f"/repos/{self.repo}")

    def _create_repository(self, name: str, description: str, private: bool) -> Dict[str, any]:
        """Create new repository with idempotency check."""
        if not name:
            return self._format_error_response("Repository name is required")
        
        # Check if repo exists
        owner = self.repo.split('/')[0]
        existing = self._make_request(f"/repos/{owner}/{name}")
        if existing.get("status") == "success":
            return self._format_success_response(
                existing.get("data"),
                "Repository already exists"
            )
        
        # Create new repository
        return self._make_request(
            "/user/repos",
            method="POST",
            data={"name": name, "description": description, "private": private}
        )

    def _list_branches(self) -> Dict[str, any]:
        """List repository branches."""
        return self._make_request(f"/repos/{self.repo}/branches")

    def _create_branch(self, name: str, base: str) -> Dict[str, any]:
        """Create new branch with idempotency check."""
        if not name:
            return self._format_error_response("Branch name is required")
        
        # Check if branch exists
        existing = self._make_request(f"/repos/{self.repo}/branches/{name}")
        if existing.get("status") == "success":
            return self._format_success_response(
                existing.get("data"),
                "Branch already exists"
            )
        
        # Get base branch SHA
        base_info = self._make_request(f"/repos/{self.repo}/git/refs/heads/{base}")
        if base_info.get("status") != "success":
            return self._format_error_response(f"Base branch '{base}' not found")
        
        base_sha = base_info["data"]["object"]["sha"]
        
        # Create new branch
        return self._make_request(
            f"/repos/{self.repo}/git/refs",
            method="POST",
            data={"ref": f"refs/heads/{name}", "sha": base_sha}
        )

    def _get_branch(self, name: str) -> Dict[str, any]:
        """Get specific branch information."""
        if not name:
            return self._format_error_response("Branch name is required")
        
        return self._make_request(f"/repos/{self.repo}/branches/{name}")

    def _list_commits(self) -> Dict[str, any]:
        """List repository commits."""
        return self._make_request(f"/repos/{self.repo}/commits")

    def _get_commit(self, sha: str) -> Dict[str, any]:
        """Get specific commit information."""
        if not sha:
            return self._format_error_response("Commit SHA is required")
        
        return self._make_request(f"/repos/{self.repo}/commits/{sha}")

    def _get_mock_response(self, endpoint: str, method: str) -> Dict[str, any]:
        """Return mock responses for testing without token."""
        mock_data = {
            "issues": [
                {
                    "number": 42,
                    "title": "Sample Issue",
                    "body": "Sample issue body",
                    "state": "open",
                    "user": {"login": "developer"}
                }
            ],
            "repository": {
                "name": self.repo.split('/')[-1],
                "full_name": self.repo,
                "description": "Sample repository",
                "html_url": f"https://github.com/{self.repo}"
            },
            "branches": [
                {"name": "main", "commit": {"sha": "abc123"}},
                {"name": "develop", "commit": {"sha": "def456"}}
            ]
        }
        
        # Simple endpoint matching for mock responses
        if "issues" in endpoint:
            data = mock_data["issues"]
        elif "repos" in endpoint and "/branches" in endpoint:
            data = mock_data["branches"]
        else:
            data = mock_data["repository"]
        
        return self._format_success_response(data, "Mock response (no GitHub token)")