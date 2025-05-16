"""
GitHub Tool - Allows agents to interact with GitHub repositories
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from tools.base_tool import ArtesanatoBaseTool
from pydantic import Field

class GitHubTool(ArtesanatoBaseTool):
    """Tool for interacting with GitHub repositories, issues, pull requests, branches, and commits."""
    
    name: str = "github_tool"
    description: str = "Tool for interacting with GitHub repositories, issues, pull requests, branches, and commits."
    token: Optional[str] = Field(default=None)
    repo: str = Field(default="artesanato-shop/artesanato-ecommerce")
    api_base_url: str = Field(default="https://api.github.com")
    headers: Dict[str, str] = Field(default_factory=dict)
    
    def __init__(self, **kwargs):
        """Initialize the GitHub tool."""
        super().__init__(**kwargs)
        self.api_base_url = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo = kwargs.get("repo", os.getenv("GITHUB_REPOSITORY", "artesanato-shop/artesanato-ecommerce"))
        self.headers = {
            "Authorization": f"token {self.token}" if self.token else "",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def _check_env_vars(self) -> None:
        """Check for required environment variables."""
        if not self.token:
            self.log("Warning: GITHUB_TOKEN not found. GitHub API calls will be mocked.")
    
    def _run(self, query: str) -> str:
        """Execute a query against the GitHub API."""
        try:
            # Parse query to determine what GitHub action to perform
            query_lower = query.lower()
            
            # Issue operations
            if "issue" in query_lower:
                if "list issues" in query_lower:
                    return self._list_issues()
                elif "create issue" in query_lower:
                    title = self._extract_param(query, "title")
                    body = self._extract_param(query, "body")
                    return self._create_issue(title, body)
                elif "update issue" in query_lower or "close issue" in query_lower:
                    issue_number = self._extract_param(query, "number")
                    state = "closed" if "close" in query_lower else self._extract_param(query, "state")
                    return self._update_issue(issue_number, state)
                else:
                    issue_number = self._extract_param(query, "number")
                    if issue_number:
                        return self._get_issue(issue_number)
                    return self._list_issues()
            
            # Pull request operations
            elif "pull request" in query_lower or "pr" in query_lower:
                if "list pull requests" in query_lower or "list prs" in query_lower:
                    return self._list_pull_requests()
                elif "create pull request" in query_lower or "create pr" in query_lower:
                    title = self._extract_param(query, "title")
                    body = self._extract_param(query, "body")
                    head = self._extract_param(query, "head") or self._extract_param(query, "branch")
                    base = self._extract_param(query, "base") or "main"
                    return self._create_pull_request(title, body, head, base)
                elif "merge pull request" in query_lower or "merge pr" in query_lower:
                    pr_number = self._extract_param(query, "number")
                    return self._merge_pull_request(pr_number)
                else:
                    pr_number = self._extract_param(query, "number")
                    if pr_number:
                        return self._get_pull_request(pr_number)
                    return self._list_pull_requests()
            
            # Repository operations
            elif "repo" in query_lower or "repository" in query_lower:
                if "create repository" in query_lower or "create repo" in query_lower:
                    name = self._extract_param(query, "name")
                    description = self._extract_param(query, "description")
                    private = "private" in query_lower
                    return self._create_repository(name, description, private)
                else:
                    return self._get_repo_info()
            
            # Branch operations
            elif "branch" in query_lower:
                if "create branch" in query_lower or "new branch" in query_lower:
                    branch_name = self._extract_param(query, "name")
                    base = self._extract_param(query, "base") or "main"
                    return self._create_branch(branch_name, base)
                elif "list branches" in query_lower:
                    return self._list_branches()
                else:
                    branch_name = self._extract_param(query, "name")
                    if branch_name:
                        return self._get_branch(branch_name)
                    return self._list_branches()
            
            # Commit operations
            elif "commit" in query_lower:
                if "list commits" in query_lower:
                    return self._list_commits()
                else:
                    commit_sha = self._extract_param(query, "sha") or self._extract_param(query, "hash")
                    if commit_sha:
                        return self._get_commit(commit_sha)
                    return self._list_commits()
            
            # Default operations based on keywords
            elif "list issues" in query_lower:
                return self._list_issues()
            elif "create issue" in query_lower:
                title = self._extract_param(query, "title")
                body = self._extract_param(query, "body")
                return self._create_issue(title, body)
            elif "get repo" in query_lower:
                return self._get_repo_info()
            elif "list pull requests" in query_lower or "list prs" in query_lower:
                return self._list_pull_requests()
            else:
                return json.dumps(self.format_response(
                    data=None,
                    error="Unsupported GitHub operation. Supported operations: list/create/update issues, list/create/merge pull requests, get/create repositories, list/create/get branches, list/get commits"
                ))
                
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._run"))
    
    def _extract_param(self, query: str, param_name: str) -> str:
        """Extract a parameter value from the query string."""
        param_start = query.find(f"{param_name}:") + len(param_name) + 1
        if param_start < len(param_name) + 1:
            return ""
            
        # Find the end of the parameter value
        next_param_pos = query[param_start:].find(":")
        param_end = param_start + next_param_pos if next_param_pos != -1 else len(query)
        
        # If there's a comma before the next param, use that as the end
        comma_pos = query[param_start:].find(",")
        if comma_pos != -1 and (comma_pos < next_param_pos or next_param_pos == -1):
            param_end = param_start + comma_pos
        
        return query[param_start:param_end].strip()
    
    # Issue operations
    
    def _get_repo_info(self) -> str:
        """Get information about the repository."""
        if not self.token:
            return self._mock_get_repo()
        
        try:
            url = f"{self.api_base_url}/repos/{self.repo}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._get_repo_info"))
    
    def _list_issues(self) -> str:
        """List open issues in the repository."""
        if not self.token:
            return self._mock_list_issues()
        
        try:
            url = f"{self.api_base_url}/repos/{self.repo}/issues"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._list_issues"))
    
    def _create_issue(self, title: str, body: str) -> str:
        """Create a new issue in the repository. Idempotent: will not create duplicate issues with the same title and body."""
        if not self.token:
            return self._mock_create_issue(title, body)
        try:
            if not title:
                return json.dumps(self.format_response(
                    data=None,
                    error="Title is required to create an issue"
                ))
            # Idempotency check: look for existing open issue with same title (and optionally body)
            url = f"{self.api_base_url}/repos/{self.repo}/issues"
            params = {"state": "open"}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            issues = response.json()
            for issue in issues:
                if issue.get("title") == title and (not body or issue.get("body") == body):
                    # Found existing issue, return it
                    return json.dumps(self.format_response(
                        data=issue,
                        error="Issue already exists with the same title and body. Returning existing issue."
                    ))
            # No duplicate found, create new issue
            payload = {
                "title": title,
                "body": body
            }
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._create_issue"))
    
    def _get_issue(self, issue_number: str) -> str:
        """Get a specific issue by number."""
        if not self.token or not issue_number:
            return self._mock_get_issue(issue_number)
        
        try:
            url = f"{self.api_base_url}/repos/{self.repo}/issues/{issue_number}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._get_issue"))
            
    def _update_issue(self, issue_number: str, state: str = None) -> str:
        """Update an issue (e.g., close it)."""
        if not self.token or not issue_number:
            return self._mock_update_issue(issue_number)
        
        try:
            url = f"{self.api_base_url}/repos/{self.repo}/issues/{issue_number}"
            payload = {}
            
            if state:
                payload["state"] = state
                
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._update_issue"))
    
    # Pull request operations
    
    def _list_pull_requests(self) -> str:
        """List open pull requests in the repository."""
        if not self.token:
            return self._mock_list_prs()
        
        try:
            url = f"{self.api_base_url}/repos/{self.repo}/pulls"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._list_pull_requests"))
    
    def _create_pull_request(self, title: str, body: str, head: str, base: str) -> str:
        """Create a new pull request. Idempotent: will not create duplicate PRs with the same title, head, and base."""
        if not self.token:
            return self._mock_create_pr(title, body, head, base)
        try:
            if not title or not head:
                return json.dumps(self.format_response(
                    data=None,
                    error="Title and head branch are required to create a pull request"
                ))
            # Idempotency check: look for existing open PR with same title, head, and base
            url = f"{self.api_base_url}/repos/{self.repo}/pulls"
            params = {"state": "open", "head": head, "base": base or "main"}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            prs = response.json()
            for pr in prs:
                if pr.get("title") == title and pr.get("head", {}).get("ref") == head and pr.get("base", {}).get("ref") == (base or "main"):
                    return json.dumps(self.format_response(
                        data=pr,
                        error="Pull request already exists with the same title, head, and base. Returning existing PR."
                    ))
            # No duplicate found, create new PR
            payload = {
                "title": title,
                "body": body,
                "head": head,
                "base": base or "main"
            }
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._create_pull_request"))
    
    def _get_pull_request(self, pr_number: str) -> str:
        """Get a specific pull request by number."""
        if not self.token or not pr_number:
            return self._mock_get_pr(pr_number)
        
        try:
            url = f"{self.api_base_url}/repos/{self.repo}/pulls/{pr_number}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._get_pull_request"))
    
    def _merge_pull_request(self, pr_number: str) -> str:
        """Merge a pull request."""
        if not self.token or not pr_number:
            return self._mock_merge_pr(pr_number)
        
        try:
            url = f"{self.api_base_url}/repos/{self.repo}/pulls/{pr_number}/merge"
            response = requests.put(url, headers=self.headers)
            response.raise_for_status()
            
            return json.dumps(self.format_response(
                data={"merged": True, "message": f"Pull request #{pr_number} successfully merged"}
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._merge_pull_request"))
    
    # Repository operations
    
    def _create_repository(self, name: str, description: str, private: bool = False) -> str:
        """Create a new repository. Idempotent: will not create duplicate repositories with the same name."""
        if not self.token or not name:
            return self._mock_create_repo(name, description)
        try:
            # Idempotency check: see if repo already exists
            url = f"{self.api_base_url}/repos/{self.repo.split('/')[0]}/{name}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return json.dumps(self.format_response(
                    data=response.json(),
                    error="Repository already exists. Returning existing repository."
                ))
            # If not found, create repo
            url = f"{self.api_base_url}/user/repos"
            payload = {
                "name": name,
                "description": description,
                "private": private
            }
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._create_repository"))
    
    # Branch operations
    
    def _list_branches(self) -> str:
        """List branches in the repository."""
        if not self.token:
            return self._mock_list_branches()
        
        try:
            url = f"{self.api_base_url}/repos/{self.repo}/branches"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._list_branches"))
    
    def _create_branch(self, branch_name: str, base: str = "main") -> str:
        """Create a new branch in the repository. Idempotent: will not create duplicate branches with the same name."""
        if not self.token or not branch_name:
            return self._mock_create_branch(branch_name)
        try:
            # Idempotency check: see if branch already exists
            url = f"{self.api_base_url}/repos/{self.repo}/branches/{branch_name}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return json.dumps(self.format_response(
                    data=response.json(),
                    error="Branch already exists. Returning existing branch."
                ))
            # If not found, create branch
            base_url = f"{self.api_base_url}/repos/{self.repo}/git/refs/heads/{base}"
            base_response = requests.get(base_url, headers=self.headers)
            base_response.raise_for_status()
            base_sha = base_response.json()["object"]["sha"]
            url = f"{self.api_base_url}/repos/{self.repo}/git/refs"
            payload = {
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha
            }
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return json.dumps(self.format_response(
                data={
                    "name": branch_name,
                    "commit": {
                        "sha": base_sha
                    }
                }
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._create_branch"))
    
    def _get_branch(self, branch_name: str) -> str:
        """Get information about a specific branch."""
        if not self.token or not branch_name:
            return self._mock_get_branch(branch_name)
        
        try:
            url = f"{self.api_base_url}/repos/{self.repo}/branches/{branch_name}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._get_branch"))
    
    # Commit operations
    
    def _list_commits(self) -> str:
        """List commits in the repository."""
        if not self.token:
            return self._mock_list_commits()
        
        try:
            url = f"{self.api_base_url}/repos/{self.repo}/commits"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._list_commits"))
    
    def _get_commit(self, commit_sha: str) -> str:
        """Get information about a specific commit."""
        if not self.token or not commit_sha:
            return self._mock_get_commit(commit_sha)
        
        try:
            url = f"{self.api_base_url}/repos/{self.repo}/commits/{commit_sha}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return json.dumps(self.format_response(
                data=response.json()
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "GitHubTool._get_commit"))
    
    # Mock responses for when GitHub token is unavailable
    def _mock_repo_info(self) -> str:
        """Return mock repository information."""
        return json.dumps(self.format_response(
            data={
                "name": "artesanato-ecommerce",
                "full_name": "artesanato-shop/artesanato-ecommerce",
                "description": "E-commerce platform for Brazilian artisanal products",
                "html_url": "https://github.com/artesanato-shop/artesanato-ecommerce",
                "stargazers_count": 42,
                "forks_count": 12,
                "open_issues_count": 5,
                "default_branch": "main"
            }
        ))
    
    def _mock_list_issues(self) -> str:
        """Return mock list of issues."""
        return json.dumps(self.format_response(
            data=[
                {
                    "number": 42,
                    "title": "Implement Missing Service Functions",
                    "state": "open",
                    "body": "Create service layer for orders and customers using Supabase",
                    "created_at": "2025-04-02T10:00:00Z",
                    "user": {"login": "backend-engineer"},
                    "labels": ["backend", "service-layer", "BE-07"]
                },
                {
                    "number": 41,
                    "title": "Validate Supabase Setup",
                    "state": "closed",
                    "body": "Validate that Supabase is correctly configured for the project",
                    "created_at": "2025-04-01T09:00:00Z",
                    "user": {"login": "backend-engineer"},
                    "labels": ["backend", "infrastructure", "BE-01"]
                },
                {
                    "number": 40,
                    "title": "Implement Core UI Components",
                    "state": "open",
                    "body": "Create reusable UI components following the design system",
                    "created_at": "2025-04-01T08:00:00Z",
                    "user": {"login": "frontend-engineer"},
                    "labels": ["frontend", "ui", "FE-02"]
                }
            ]
        ))
    
    def _mock_create_issue(self, title: str, body: str) -> str:
        """Return mock response for issue creation."""
        return json.dumps(self.format_response(
            data={
                "number": 43,
                "title": title,
                "state": "open",
                "body": body,
                "created_at": "2025-05-05T10:00:00Z",
                "updated_at": "2025-05-05T10:00:00Z",
                "user": {"login": "ai-agent"},
                "html_url": f"https://github.com/{self.repo}/issues/43"
            }
        ))
    
    def _mock_get_issue(self, issue_number: str) -> str:
        """Return mock response for getting an issue."""
        issue_num = issue_number or "42"
        return json.dumps(self.format_response(
            data={
                "id": 1,
                "number": int(issue_num),
                "title": "Implement Missing Service Functions",
                "body": "Create service layer for orders and customers using Supabase",
                "state": "open",
                "assignee": "backend-engineer",
                "labels": ["backend", "service-layer", "BE-07"],
                "created_at": "2025-04-02T10:00:00Z",
                "updated_at": "2025-04-02T10:00:00Z",
                "html_url": f"https://github.com/{self.repo}/issues/{issue_num}"
            }
        ))
    
    def _mock_update_issue(self, issue_number: str) -> str:
        """Return mock response for updating an issue."""
        issue_num = issue_number or "42"
        return json.dumps(self.format_response(
            data={
                "id": 1,
                "number": int(issue_num),
                "title": "Implement Missing Service Functions",
                "body": "Create service layer for orders and customers using Supabase",
                "state": "closed",
                "assignee": "backend-engineer",
                "labels": ["backend", "service-layer", "BE-07", "completed"],
                "created_at": "2025-04-02T10:00:00Z",
                "updated_at": "2025-05-05T15:00:00Z",
                "html_url": f"https://github.com/{self.repo}/issues/{issue_num}"
            }
        ))
    
    def _mock_list_prs(self) -> str:
        """Return mock list of pull requests."""
        return json.dumps(self.format_response(
            data=[
                {
                    "number": 14,
                    "title": "Implement Missing Service Functions",
                    "state": "open",
                    "body": "Closes #42",
                    "user": {"login": "backend-engineer"},
                    "base": {"ref": "main"},
                    "head": {"ref": "feature/missing-service-functions"},
                    "created_at": "2025-04-02T15:30:00Z",
                    "updated_at": "2025-04-02T15:30:00Z",
                    "html_url": f"https://github.com/{self.repo}/pull/14"
                },
                {
                    "number": 13,
                    "title": "Implement Core UI Components",
                    "state": "open",
                    "body": "Closes #40",
                    "user": {"login": "frontend-engineer"},
                    "base": {"ref": "main"},
                    "head": {"ref": "feature/core-ui-components"},
                    "created_at": "2025-04-01T15:00:00Z",
                    "updated_at": "2025-04-01T15:00:00Z",
                    "html_url": f"https://github.com/{self.repo}/pull/13"
                }
            ]
        ))
    
    def _mock_create_pr(self, title: str, body: str, head: str, base: str) -> str:
        """Return mock response for pull request creation."""
        return json.dumps(self.format_response(
            data={
                "id": 1,
                "number": 15,
                "title": title,
                "body": body,
                "state": "open",
                "user": {"login": "ai-agent"},
                "base": {"ref": base or "main"},
                "head": {"ref": head},
                "created_at": "2025-05-05T15:30:00Z",
                "updated_at": "2025-05-05T15:30:00Z",
                "html_url": f"https://github.com/{self.repo}/pull/15"
            }
        ))
    
    def _mock_get_pr(self, pr_number: str) -> str:
        """Return mock response for getting a pull request."""
        pr_num = pr_number or "14"
        return json.dumps(self.format_response(
            data={
                "id": 1,
                "number": int(pr_num),
                "title": "Implement Missing Service Functions",
                "body": "Closes #42",
                "state": "open",
                "user": {"login": "backend-engineer"},
                "base": {"ref": "main"},
                "head": {"ref": "feature/missing-service-functions"},
                "created_at": "2025-04-02T15:30:00Z",
                "updated_at": "2025-04-02T15:30:00Z",
                "html_url": f"https://github.com/{self.repo}/pull/{pr_num}"
            }
        ))
    
    def _mock_merge_pr(self, pr_number: str) -> str:
        """Return mock response for merging a pull request."""
        pr_num = pr_number or "14"
        return json.dumps(self.format_response(
            data={
                "id": 1,
                "number": int(pr_num),
                "title": "Implement Missing Service Functions",
                "body": "Closes #42",
                "state": "closed",
                "merged": True,
                "user": {"login": "backend-engineer"},
                "base": {"ref": "main"},
                "head": {"ref": "feature/missing-service-functions"},
                "created_at": "2025-04-02T15:30:00Z",
                "updated_at": "2025-05-05T16:30:00Z",
                "merged_at": "2025-05-05T16:30:00Z",
                "html_url": f"https://github.com/{self.repo}/pull/{pr_num}"
            }
        ))
    
    def _mock_create_repo(self, name: str, description: str) -> str:
        """Return mock response for repository creation."""
        repo_name = name or "new-repo"
        return json.dumps(self.format_response(
            data={
                "id": 1,
                "name": repo_name,
                "full_name": f"artesanato-shop/{repo_name}",
                "private": False,
                "description": description or "E-commerce platform for Brazilian artisanal products",
                "created_at": "2025-05-05T09:00:00Z",
                "updated_at": "2025-05-05T09:00:00Z",
                "html_url": f"https://github.com/artesanato-shop/{repo_name}",
                "clone_url": f"https://github.com/artesanato-shop/{repo_name}.git"
            }
        ))
    
    def _mock_get_repo(self) -> str:
        """Return mock response for getting repository information."""
        return json.dumps(self.format_response(
            data={
                "id": 1,
                "name": "artesanato-ecommerce",
                "full_name": "artesanato-shop/artesanato-ecommerce",
                "private": False,
                "description": "E-commerce platform for Brazilian artisanal products",
                "created_at": "2025-04-01T09:00:00Z",
                "updated_at": "2025-05-05T09:00:00Z",
                "html_url": "https://github.com/artesanato-shop/artesanato-ecommerce",
                "clone_url": "https://github.com/artesanato-shop/artesanato-ecommerce.git",
                "default_branch": "main",
                "open_issues_count": 10,
                "forks_count": 5,
                "watchers_count": 15
            }
        ))
    
    def _mock_list_branches(self) -> str:
        """Return mock response for listing branches."""
        return json.dumps(self.format_response(
            data=[
                {
                    "name": "main",
                    "commit": {
                        "sha": "123456789abcdef",
                        "url": f"https://api.github.com/repos/{self.repo}/commits/123456789abcdef"
                    },
                    "protected": True
                },
                {
                    "name": "feature/missing-service-functions",
                    "commit": {
                        "sha": "abcdef123456789",
                        "url": f"https://api.github.com/repos/{self.repo}/commits/abcdef123456789"
                    },
                    "protected": False
                },
                {
                    "name": "feature/core-ui-components",
                    "commit": {
                        "sha": "987654321fedcba",
                        "url": f"https://api.github.com/repos/{self.repo}/commits/987654321fedcba"
                    },
                    "protected": False
                }
            ]
        ))
    
    def _mock_create_branch(self, branch_name: str) -> str:
        """Return mock response for branch creation."""
        name = branch_name or "feature/new-branch"
        return json.dumps(self.format_response(
            data={
                "name": name,
                "commit": {
                    "sha": "abcdef123456789",
                    "url": f"https://api.github.com/repos/{self.repo}/commits/abcdef123456789"
                },
                "protected": False
            }
        ))
    
    def _mock_get_branch(self, branch_name: str) -> str:
        """Return mock response for getting a branch."""
        name = branch_name or "feature/missing-service-functions"
        return json.dumps(self.format_response(
            data={
                "name": name,
                "commit": {
                    "sha": "abcdef123456789",
                    "url": f"https://api.github.com/repos/{self.repo}/commits/abcdef123456789"
                },
                "protected": False
            }
        ))
    
    def _mock_list_commits(self) -> str:
        """Return mock response for listing commits."""
        return json.dumps(self.format_response(
            data=[
                {
                    "sha": "abcdef123456789",
                    "commit": {
                        "message": "Implement customer service functions",
                        "author": {
                            "name": "Backend Engineer",
                            "email": "backend@example.com",
                            "date": "2025-04-02T16:00:00Z"
                        }
                    },
                    "author": {"login": "backend-engineer"},
                    "html_url": f"https://github.com/{self.repo}/commit/abcdef123456789"
                },
                {
                    "sha": "123456789abcdef",
                    "commit": {
                        "message": "Implement core UI components",
                        "author": {
                            "name": "Frontend Engineer",
                            "email": "frontend@example.com",
                            "date": "2025-04-02T15:00:00Z"
                        }
                    },
                    "author": {"login": "frontend-engineer"},
                    "html_url": f"https://github.com/{self.repo}/commit/123456789abcdef"
                }
            ]
        ))
    
    def _mock_get_commit(self, commit_sha: str) -> str:
        """Return mock response for getting a commit."""
        sha = commit_sha or "abcdef123456789"
        return json.dumps(self.format_response(
            data={
                "sha": sha,
                "commit": {
                    "message": "Implement customer service functions",
                    "author": {
                        "name": "Backend Engineer",
                        "email": "backend@example.com",
                        "date": "2025-04-02T16:00:00Z"
                    },
                    "committer": {
                        "name": "Backend Engineer",
                        "email": "backend@example.com",
                        "date": "2025-04-02T16:00:00Z"
                    }
                },
                "author": {"login": "backend-engineer"},
                "files": [
                    {
                        "filename": "lib/services/customerService.ts",
                        "status": "added",
                        "additions": 120,
                        "deletions": 0
                    }
                ],
                "html_url": f"https://github.com/{self.repo}/commit/{sha}"
            }
        ))