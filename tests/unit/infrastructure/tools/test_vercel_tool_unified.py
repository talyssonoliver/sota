"""
Comprehensive tests for the unified Vercel Tool with Git integration.
Tests all major functionality including Deploy Hooks and Git repository connections.
"""

import json
import pytest
from unittest.mock import Mock, patch
from src.infrastructure.tools.external.vercel_tool import VercelTool


class TestVercelToolUnified:
    """Test suite for the unified Vercel Tool with Git integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool = VercelTool()
        self.tool.token = "test-vercel-token"
        self.tool.team_id = "test-team-id"
        self.tool.project_id = "test-project-id"
        self.tool.headers = {
            "Authorization": "Bearer test-vercel-token",
            "Content-Type": "application/json"
        }

    def test_init_with_token(self):
        """Test tool initialization with token."""
        tool = VercelTool()
        assert tool.name == "vercel_tool"
        assert tool.api_base_url == "https://api.vercel.com"
        assert len(tool.commands) == 8  # All command handlers

    def test_extract_param(self):
        """Test parameter extraction from query strings."""
        query = "create deployment project:test-proj branch:main commit:abc123"
        
        assert self.tool._extract_param(query, "project") == "test-proj"
        assert self.tool._extract_param(query, "branch") == "main"
        assert self.tool._extract_param(query, "commit") == "abc123"
        assert self.tool._extract_param(query, "nonexistent") is None

    def test_project_command_routing(self):
        """Test project command routing."""
        from src.platform.tools.vercel_tool_unified import ProjectCommand
        
        command = ProjectCommand(self.tool)
        
        assert command.can_handle("create project")
        assert command.can_handle("list projects")
        assert command.can_handle("get project")
        assert command.can_handle("delete project")
        assert not command.can_handle("create deployment")

    def test_deployment_command_routing(self):
        """Test deployment command routing."""
        from src.platform.tools.vercel_tool_unified import DeploymentCommand
        
        command = DeploymentCommand(self.tool)
        
        assert command.can_handle("create deployment")
        assert command.can_handle("trigger deployment")
        assert command.can_handle("list deployments")
        assert not command.can_handle("create project")

    def test_deploy_hook_command_routing(self):
        """Test deploy hook command routing."""
        from src.platform.tools.vercel_tool_unified import DeployHookCommand
        
        command = DeployHookCommand(self.tool)
        
        assert command.can_handle("create hook")
        assert command.can_handle("list hooks")
        assert command.can_handle("trigger hook")
        assert command.can_handle("delete hook")
        assert not command.can_handle("create project")

    def test_git_integration_command_routing(self):
        """Test Git integration command routing."""
        from src.platform.tools.vercel_tool_unified import GitIntegrationCommand
        
        command = GitIntegrationCommand(self.tool)
        
        assert command.can_handle("connect git")
        assert command.can_handle("git status")
        assert command.can_handle("disconnect git")
        assert command.can_handle("link repository")
        assert not command.can_handle("create project")

    @patch('requests.post')
    def test_create_deploy_hook_success(self, mock_post):
        """Test successful deploy hook creation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "hook_123",
            "name": "test-hook",
            "url": "https://api.vercel.com/v1/integrations/deploy-hooks/hook_123/prj_123",
            "ref": "main"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.tool._create_deploy_hook("prj_123", "test-hook", "main")
        result_data = json.loads(result)

        assert result_data["data"]["name"] == "test-hook"
        assert result_data["data"]["ref"] == "main"
        assert result_data["error"] is None

    @patch('requests.get')
    def test_list_deploy_hooks_success(self, mock_get):
        """Test successful deploy hooks listing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hooks": [
                {
                    "id": "hook_123",
                    "name": "deployment-main",
                    "url": "https://api.vercel.com/v1/integrations/deploy-hooks/hook_123/prj_123",
                    "ref": "main"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.tool._list_deploy_hooks("prj_123")
        result_data = json.loads(result)

        assert result_data["data"]["hooks"] is not None
        assert len(result_data["data"]["hooks"]) == 1
        assert result_data["data"]["hooks"][0]["name"] == "deployment-main"
        assert result_data["error"] is None

    @patch('requests.post')
    def test_trigger_deploy_hook_success(self, mock_post):
        """Test successful deploy hook triggering."""
        # Mock the list_deploy_hooks call first
        with patch.object(self.tool, '_list_deploy_hooks') as mock_list:
            mock_list.return_value = json.dumps({
                "success": True,
                "data": {
                    "hooks": [
                        {
                            "name": "test-hook",
                            "url": "https://api.vercel.com/v1/integrations/deploy-hooks/hook_123/prj_123"
                        }
                    ]
                }
            })

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = self.tool._trigger_deploy_hook("prj_123", "test-hook", "main")
            result_data = json.loads(result)

            assert result_data["data"]["success"] is True
            assert "triggered successfully" in result_data["data"]["message"]

    @patch('requests.patch')
    def test_connect_git_repository_success(self, mock_patch):
        """Test successful Git repository connection."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "prj_123",
            "link": {
                "type": "github",
                "repo": "user/repo",
                "gitSource": {
                    "type": "github",
                    "ref": "main"
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_patch.return_value = mock_response

        result = self.tool._connect_git_repository("prj_123", "https://github.com/user/repo", "main")
        result_data = json.loads(result)

        assert result_data["data"]["link"]["repo"] == "user/repo"
        assert result_data["data"]["link"]["type"] == "github"
        assert result_data["error"] is None

    def test_connect_git_repository_invalid_url(self):
        """Test Git repository connection with invalid URL."""
        result = self.tool._connect_git_repository("prj_123", "invalid-url", "main")
        result_data = json.loads(result)

        assert result_data["data"] is None
        assert result_data["error"] is not None
        assert "Invalid GitHub repository URL format" in result_data["error"]

    @patch('requests.patch')
    def test_disconnect_git_repository_success(self, mock_patch):
        """Test successful Git repository disconnection."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_patch.return_value = mock_response

        result = self.tool._disconnect_git_repository("prj_123")
        result_data = json.loads(result)

        assert result_data["data"]["success"] is True
        assert "disconnected successfully" in result_data["data"]["message"]

    def test_get_git_integration_status_with_connection(self):
        """Test Git integration status with active connection."""
        # Clear token to force mock usage 
        original_token = self.tool.token
        self.tool.token = ""
        
        try:
            result = self.tool._get_git_integration_status("prj_123")
            result_data = json.loads(result)

            assert result_data["data"]["connected"] is True
            assert result_data["data"]["provider"] == "github"
            assert result_data["data"]["repository"] == "user/artesanato-ecommerce"
            assert result_data["error"] is None
        finally:
            # Restore token
            self.tool.token = original_token

    def test_get_git_integration_status_without_connection(self):
        """Test Git integration status without connection."""
        with patch.object(self.tool, '_get_project') as mock_get_project:
            mock_get_project.return_value = json.dumps({
                "success": True,
                "data": {}  # No link field
            })

            result = self.tool._get_git_integration_status("prj_123")
            result_data = json.loads(result)

            assert result_data["data"]["connected"] is False
            assert result_data["error"] is None

    @patch('requests.post')
    def test_create_deployment_with_git_integration(self, mock_post):
        """Test deployment creation with Git integration."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "dpl_123",
            "url": "test-app.vercel.app",
            "target": "production",
            "meta": {
                "githubCommitSha": "abcdef123456789"
            },
            "gitSource": {
                "type": "github",
                "ref": "main",
                "sha": "abc123"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.tool._create_deployment("prj_123", "main", "abc123")
        result_data = json.loads(result)

        assert result_data["data"]["target"] == "production"
        assert result_data["data"]["meta"]["githubCommitSha"] == "abcdef123456789"
        assert result_data["error"] is None

    @patch('requests.post')
    def test_create_project_with_git_repo(self, mock_post):
        """Test project creation with Git repository integration."""
        # Mock the GET request to check if project exists (returns 404)
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 404

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "prj_123",
                "name": "test-project",
                "framework": "nextjs",
                "gitRepository": {
                    "type": "github",
                    "repo": "user/test-project"
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = self.tool._create_project("test-project", "nextjs", "https://github.com/user/test-project")
            result_data = json.loads(result)

            assert result_data["data"]["name"] == "test-project"
            assert result_data["error"] is None

    def test_run_with_deploy_hook_query(self):
        """Test _run method with deploy hook query."""
        with patch.object(self.tool, '_create_deploy_hook') as mock_create:
            mock_create.return_value = json.dumps({"success": True, "data": {}})

            result = self.tool._run("create hook name:test-hook project:prj_123 branch:main")
            assert '"success": true' in result

    def test_run_with_git_integration_query(self):
        """Test _run method with Git integration query."""
        # Clear token to force mock usage
        original_token = self.tool.token
        self.tool.token = ""
        
        try:
            result = self.tool._run("connect git repo:https://github.com/user/repo project:prj_123")
            result_data = json.loads(result)
            assert result_data["data"]["success"] is True
            assert "Git repository" in result_data["data"]["message"]
        finally:
            # Restore token
            self.tool.token = original_token

    def test_run_with_trigger_deployment_hook_query(self):
        """Test _run method with deployment hook trigger query."""
        # Clear token to force mock usage
        original_token = self.tool.token
        self.tool.token = ""
        
        try:
            result = self.tool._run("trigger deployment hook project:prj_123 hook_name:test-hook")
            result_data = json.loads(result)
            assert result_data["error"] is None
            # Trigger should create a deployment
            assert result_data["data"]["name"] is not None
        finally:
            # Restore token
            self.tool.token = original_token

    def test_enhanced_deployment_with_commit_sha(self):
        """Test enhanced deployment creation with specific commit SHA."""
        with patch.object(self.tool, '_create_deployment') as mock_create:
            mock_create.return_value = json.dumps({
                "success": True,
                "data": {
                    "id": "dpl_123",
                    "gitSource": {"sha": "abc123def456"}
                }
            })

            result = self.tool._run("create deployment project:prj_123 branch:feature commit:abc123def456")
            result_data = json.loads(result)

            assert result_data["data"] is not None
            mock_create.assert_called_once_with("prj_123", "feature", "abc123def456")

    def test_mock_responses_without_token(self):
        """Test that mock responses are returned when no token is present."""
        tool_without_token = VercelTool()
        tool_without_token.token = ""

        # Test various mock methods
        result = tool_without_token._create_deploy_hook("prj_123", "test-hook", "main")
        result_data = json.loads(result)
        assert result_data["data"]["name"] == "test-hook"
        assert result_data["error"] is None

        result = tool_without_token._connect_git_repository("prj_123", "https://github.com/user/repo", "main")
        result_data = json.loads(result)
        assert result_data["data"]["success"] is True
        assert result_data["error"] is None

        result = tool_without_token._get_git_integration_status("prj_123")
        result_data = json.loads(result)
        assert result_data["data"]["connected"] is True
        assert result_data["error"] is None

    def test_input_validation(self):
        """Test input validation for query parameter."""
        with pytest.raises(Exception):
            # This should trigger a ValidationError which gets handled
            result = self.tool._run("")  # Empty query
            # The error should be handled gracefully and return an error response
            result_data = json.loads(result)
            assert result_data["success"] is False

    def test_unsupported_operation(self):
        """Test handling of unsupported operations."""
        result = self.tool._run("unsupported operation")
        result_data = json.loads(result)

        assert result_data["data"] is None
        assert result_data["error"] is not None
        assert "Unsupported Vercel operation" in result_data["error"]

    def test_domain_and_env_commands_compatibility(self):
        """Test that domain and environment commands still work with new structure."""
        # Clear token to force mock usage
        original_token = self.tool.token
        self.tool.token = ""
        
        try:
            # Test domain command - "domain" should match DomainCommand before ProjectCommand
            result = self.tool._run("add domain name:example.com project:prj_123")
            result_data = json.loads(result)
            assert result_data["error"] is None

            # Test environment command - "env" should match EnvironmentCommand before ProjectCommand  
            result = self.tool._run("add env name:API_KEY value:secret123 project:prj_123")
            result_data = json.loads(result)
            assert result_data["error"] is None
        finally:
            # Restore token
            self.tool.token = original_token

    def test_error_handling_in_git_operations(self):
        """Test error handling in Git operations."""
        with patch('requests.patch') as mock_patch:
            mock_patch.side_effect = Exception("Network error")

            result = self.tool._connect_git_repository("prj_123", "https://github.com/user/repo", "main")
            result_data = json.loads(result)

            assert result_data["data"] is None
            assert result_data["error"] is not None


class TestVercelToolBackwardCompatibility:
    """Test backward compatibility with existing usage patterns."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool = VercelTool()

    def test_original_queries_still_work(self):
        """Test that original query patterns still work."""
        original_queries = [
            "list projects",
            "create project name:test-project",
            "list deployments",
            "create deployment project:prj_123",
            "add domain name:example.com project:prj_123",
            "list env variables project:prj_123",
            "get logs id:dpl_123"
        ]

        for query in original_queries:
            try:
                result = self.tool._run(query)
                result_data = json.loads(result)
                # Should not raise exceptions and should return a response
                assert "success" in result_data or "error" in result_data
            except Exception as e:
                pytest.fail(f"Query '{query}' failed with: {e}")

    def test_tool_attributes_unchanged(self):
        """Test that critical tool attributes remain unchanged."""
        assert self.tool.name == "vercel_tool"
        assert hasattr(self.tool, 'token')
        assert hasattr(self.tool, 'team_id')
        assert hasattr(self.tool, 'project_id')
        assert hasattr(self.tool, 'api_base_url')
        assert self.tool.api_base_url == "https://api.vercel.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
