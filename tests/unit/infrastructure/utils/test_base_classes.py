"""
Test suite for base classes that provide common patterns and reduce code duplication.
"""

import json
import os
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.infrastructure.utils.base_classes import (
    BaseComponent, BaseTool, BaseAPITool, BaseValidator, 
    BaseWorkflow, BaseService
)


class TestBaseComponent:
    """Test BaseComponent functionality."""
    
    def test_component_initialization(self):
        """Test basic component initialization."""
        class TestComponent(BaseComponent):
            def _get_default_config(self):
                return {"test_setting": "default_value"}
        
        component = TestComponent(name="test_component")
        
        assert component.name == "test_component"
        assert component.config["test_setting"] == "default_value"
        assert isinstance(component.initialized_at, datetime)
        assert hasattr(component, "logger")
    
    def test_component_config_loading(self):
        """Test configuration loading from file and kwargs."""
        class TestComponent(BaseComponent):
            def _get_default_config(self):
                return {"default": "value", "override_me": "default"}
        
        # Test with kwargs override
        component = TestComponent(
            override_me="overridden",
            new_setting="added"
        )
        
        assert component.config["default"] == "value"
        assert component.config["override_me"] == "overridden"
        assert component.config["new_setting"] == "added"
    
    def test_component_config_from_file(self):
        """Test configuration loading from JSON file."""
        class TestComponent(BaseComponent):
            def _get_default_config(self):
                return {"default": "value"}
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {"file_setting": "from_file", "override_me": "file_value"}
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            component = TestComponent(
                config_path=config_path,
                override_me="kwargs_value"
            )
            
            assert component.config["file_setting"] == "from_file"
            assert component.config["override_me"] == "kwargs_value"  # kwargs override file
            assert component.config["default"] == "value"  # default preserved
        finally:
            os.unlink(config_path)
    
    def test_component_status(self):
        """Test component status reporting."""
        class TestComponent(BaseComponent):
            def _get_default_config(self):
                return {}
        
        component = TestComponent()
        status = component.get_status()
        
        assert status["name"] == "TestComponent"
        assert status["config_loaded"] is True
        assert status["status"] == "active"
        assert "initialized_at" in status


class TestBaseTool:
    """Test BaseTool functionality."""
    
    def test_tool_initialization(self):
        """Test tool initialization with default config."""
        class TestTool(BaseTool):
            def _execute(self, *args, **kwargs):
                return {"result": "test"}
        
        tool = TestTool()
        
        assert tool.config["timeout"] == 30
        assert tool.config["retries"] == 3
        assert "test_mode" in tool.config
    
    def test_tool_execution_success(self):
        """Test successful tool execution."""
        class TestTool(BaseTool):
            def _execute(self, input_data):
                return input_data.upper()
        
        tool = TestTool()
        result = tool.execute("hello")
        
        assert result == "HELLO"
    
    def test_tool_execution_error_handling(self):
        """Test tool error handling."""
        class TestTool(BaseTool):
            def _execute(self, *args, **kwargs):
                raise ValueError("Test error")
        
        tool = TestTool()
        result = tool.execute("test")
        
        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "Test error" in result["errors"][0]
    
    def test_tool_validation(self):
        """Test tool configuration validation."""
        class TestTool(BaseTool):
            def _get_required_fields(self):
                return ["required_field"]
            
            def _execute(self, *args, **kwargs):
                return "success"
        
        # Should log warning but not fail in test mode
        with patch('src.infrastructure.utils.base_classes.is_test_mode', return_value=True):
            tool = TestTool()  # Missing required_field but in test mode
            assert tool.name == "TestTool"
    
    def test_tool_response_formatting(self):
        """Test response formatting methods."""
        class TestTool(BaseTool):
            def _execute(self, *args, **kwargs):
                return self._format_success_response(
                    data={"key": "value"}, 
                    message="Custom success"
                )
        
        tool = TestTool()
        result = tool.execute("test")
        
        assert result["status"] == "success"
        assert result["data"]["key"] == "value"
        assert result["message"] == "Custom success"


class TestBaseAPITool:
    """Test BaseAPITool functionality."""
    
    def test_api_tool_initialization(self):
        """Test API tool initialization."""
        class TestAPITool(BaseAPITool):
            def _execute(self, *args, **kwargs):
                return {"api": "response"}
        
        tool = TestAPITool()
        
        assert tool.config["base_url"] == "http://localhost:3000"
        assert tool.config["verify_ssl"] is True
        assert tool.config["timeout"] == 30
    
    @patch.dict(os.environ, {"TEST_API_TOKEN": "test_token_123"})
    def test_credential_loading(self):
        """Test API credential loading from environment."""
        class TestAPITool(BaseAPITool):
            def _execute(self, *args, **kwargs):
                return {"token": self.token}
        
        tool = TestAPITool(name="test_api")
        
        # Should find TEST_API_TOKEN or fallback to API_TOKEN
        assert tool.token is not None
    
    def test_header_generation(self):
        """Test API header generation."""
        class TestAPITool(BaseAPITool):
            def _execute(self, *args, **kwargs):
                return self._get_headers()
        
        tool = TestAPITool(name="test_api")
        tool.token = "test_token"
        
        headers = tool._get_headers()
        
        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "Bearer test_token"
        assert "User-Agent" in headers
    
    def test_bearer_token_handling(self):
        """Test Bearer token prefix handling."""
        class TestAPITool(BaseAPITool):
            def _execute(self, *args, **kwargs):
                return self._get_headers()
        
        tool = TestAPITool()
        tool.token = "Bearer existing_prefix"
        
        headers = tool._get_headers()
        assert headers["Authorization"] == "Bearer existing_prefix"  # Don't double-prefix


class TestBaseValidator:
    """Test BaseValidator functionality."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        class TestValidator(BaseValidator):
            def _validate_target(self, target):
                if target == "invalid":
                    self.add_issue("error", "Invalid target", "test_location")
        
        validator = TestValidator()
        
        assert validator.issues == []
        assert validator.config["strict_mode"] is False
        assert validator.config["max_issues"] == 1000
    
    def test_validation_success(self):
        """Test successful validation."""
        class TestValidator(BaseValidator):
            def _validate_target(self, target):
                pass  # No issues added
        
        validator = TestValidator()
        result = validator.validate("valid_target")
        
        assert result["valid"] is True
        assert result["issues"] == []
        assert result["total_issues"] == 0
        assert "timestamp" in result
    
    def test_validation_with_issues(self):
        """Test validation with issues found."""
        class TestValidator(BaseValidator):
            def _validate_target(self, target):
                self.add_issue("warning", "Minor issue", "line 1")
                self.add_issue("error", "Major issue", "line 5", "Fix this")
        
        validator = TestValidator()
        result = validator.validate("problematic_target")
        
        assert result["valid"] is False
        assert len(result["issues"]) == 2
        assert result["total_issues"] == 2
        
        # Check issue structure
        warning_issue = result["issues"][0]
        assert warning_issue["severity"] == "warning"
        assert warning_issue["message"] == "Minor issue"
        assert warning_issue["location"] == "line 1"
        
        error_issue = result["issues"][1]
        assert error_issue["fix_suggestion"] == "Fix this"
    
    def test_validation_error_handling(self):
        """Test validation error handling."""
        class TestValidator(BaseValidator):
            def _validate_target(self, target):
                raise RuntimeError("Validation crashed")
        
        validator = TestValidator()
        result = validator.validate("any_target")
        
        assert result["valid"] is False
        assert "error" in result
        assert "Validation crashed" in result["error"]
    
    def test_max_issues_limit(self):
        """Test maximum issues limit."""
        class TestValidator(BaseValidator):
            def _validate_target(self, target):
                for i in range(10):
                    self.add_issue("info", f"Issue {i}")
        
        validator = TestValidator()
        validator.config["max_issues"] = 5
        result = validator.validate("target")
        
        assert len(result["issues"]) == 5  # Limited to max_issues
        assert result["total_issues"] == 10  # But total count is accurate


class TestBaseWorkflow:
    """Test BaseWorkflow functionality."""
    
    @pytest.mark.asyncio
    async def test_workflow_initialization(self):
        """Test workflow initialization."""
        class TestWorkflow(BaseWorkflow):
            async def _execute_step(self, step, context):
                return {"success": True, "step": step["name"]}
        
        workflow = TestWorkflow()
        
        assert workflow.state == "initialized"
        assert workflow.steps == []
        assert workflow.config["timeout"] == 300
    
    @pytest.mark.asyncio
    async def test_workflow_step_execution(self):
        """Test workflow step execution."""
        class TestWorkflow(BaseWorkflow):
            async def _execute_step(self, step, context):
                handler = step["handler"]
                return {"success": True, "result": await handler(context)}
        
        async def step_handler(context):
            return f"Processed {context.get('input', 'nothing')}"
        
        workflow = TestWorkflow()
        workflow.add_step("test_step", step_handler)
        
        result = await workflow.execute_workflow({"input": "test_data"})
        
        assert result["success"] is True
        assert len(result["results"]) == 1
        assert result["results"][0]["result"] == "Processed test_data"
    
    @pytest.mark.asyncio
    async def test_workflow_failure_handling(self):
        """Test workflow failure handling."""
        class TestWorkflow(BaseWorkflow):
            async def _execute_step(self, step, context):
                if step["name"] == "failing_step":
                    return {"success": False, "error": "Step failed"}
                return {"success": True}
        
        workflow = TestWorkflow()
        workflow.add_step("good_step", lambda ctx: "ok")
        workflow.add_step("failing_step", lambda ctx: "fail")
        workflow.add_step("never_reached", lambda ctx: "no")
        
        result = await workflow.execute_workflow()
        
        assert result["success"] is False
        assert len(result["results"]) == 2  # Stopped after failure
        assert workflow.state == "completed"
    
    @pytest.mark.asyncio
    async def test_workflow_continue_on_error(self):
        """Test workflow continuing on error when configured."""
        class TestWorkflow(BaseWorkflow):
            async def _execute_step(self, step, context):
                if step["name"] == "failing_step":
                    return {"success": False, "error": "Step failed"}
                return {"success": True}
        
        workflow = TestWorkflow()
        workflow.config["continue_on_error"] = True
        workflow.add_step("good_step", lambda ctx: "ok")
        workflow.add_step("failing_step", lambda ctx: "fail")
        workflow.add_step("final_step", lambda ctx: "done")
        
        result = await workflow.execute_workflow()
        
        assert result["success"] is False  # Overall failure due to failed step
        assert len(result["results"]) == 3  # But all steps executed


class TestBaseService:
    """Test BaseService functionality."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        class TestService(BaseService):
            def _start_service(self):
                self.started = True
            
            def _stop_service(self):
                self.started = False
        
        service = TestService()
        
        assert service.status == "running"  # auto_start is True by default
        assert hasattr(service, 'started')
    
    def test_service_lifecycle(self):
        """Test service start/stop lifecycle."""
        class TestService(BaseService):
            def __init__(self, **kwargs):
                self.started = False
                super().__init__(**kwargs)
            
            def _start_service(self):
                self.started = True
            
            def _stop_service(self):
                self.started = False
        
        service = TestService(auto_start=False)
        assert service.status == "stopped"
        
        # Test start
        result = service.start()
        assert result is True
        assert service.status == "running"
        assert service.started is True
        
        # Test stop
        result = service.stop()
        assert result is True
        assert service.status == "stopped"
        assert service.started is False
    
    def test_service_start_failure(self):
        """Test service start failure handling."""
        class TestService(BaseService):
            def _start_service(self):
                raise RuntimeError("Service failed to start")
            
            def _stop_service(self):
                pass
        
        service = TestService(auto_start=False)
        result = service.start()
        
        assert result is False
        assert service.status == "failed"
    
    def test_service_health_check(self):
        """Test service health check."""
        class TestService(BaseService):
            def _start_service(self):
                pass
            
            def _stop_service(self):
                pass
            
            def _health_check(self):
                return {"status": "healthy", "uptime": "5 minutes"}
        
        service = TestService()
        health = service.health_check()
        
        assert health["healthy"] is True
        assert health["status"] == "running"
        assert health["data"]["status"] == "healthy"
        assert "timestamp" in health
    
    def test_service_health_check_failure(self):
        """Test service health check failure."""
        class TestService(BaseService):
            def _start_service(self):
                pass
            
            def _stop_service(self):
                pass
            
            def _health_check(self):
                raise RuntimeError("Health check failed")
        
        service = TestService()
        health = service.health_check()
        
        assert health["healthy"] is False
        assert "error" in health
        assert "Health check failed" in health["error"]


@pytest.fixture
def temp_config_file():
    """Fixture to create temporary config file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {
            "api_url": "https://test.api.com",
            "timeout": 60,
            "debug": True
        }
        json.dump(config, f)
        yield f.name
    os.unlink(f.name)


class TestBaseClassesIntegration:
    """Integration tests for base classes working together."""
    
    def test_api_tool_with_validator(self, temp_config_file):
        """Test API tool using validator for input validation."""
        class InputValidator(BaseValidator):
            def _validate_target(self, target):
                if not isinstance(target, dict):
                    self.add_issue("error", "Input must be dictionary")
                elif "required_field" not in target:
                    self.add_issue("error", "Missing required_field")
        
        class ValidatedAPITool(BaseAPITool):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.validator = InputValidator()
            
            def _execute(self, input_data):
                # Validate input first
                validation_result = self.validator.validate(input_data)
                if not validation_result["valid"]:
                    return self._format_error_response(
                        f"Validation failed: {validation_result['issues']}"
                    )
                
                return self._format_success_response(
                    {"processed": input_data},
                    "Input validated and processed"
                )
        
        tool = ValidatedAPITool(config_path=temp_config_file)
        
        # Test invalid input
        result = tool.execute("invalid_string")
        assert result["status"] == "error"
        
        # Test valid input
        result = tool.execute({"required_field": "value"})
        assert result["status"] == "success"
        assert result["data"]["processed"]["required_field"] == "value"
    
    @pytest.mark.asyncio
    async def test_service_with_workflow(self):
        """Test service that manages workflow execution."""
        class WorkflowService(BaseService):
            def __init__(self, **kwargs):
                self.workflow = None
                super().__init__(**kwargs)
            
            def _start_service(self):
                class ServiceWorkflow(BaseWorkflow):
                    async def _execute_step(self, step, context):
                        return {"success": True, "step": step["name"]}
                
                self.workflow = ServiceWorkflow()
                self.workflow.add_step("init", lambda ctx: "initialized")
                self.workflow.add_step("process", lambda ctx: "processed")
            
            def _stop_service(self):
                self.workflow = None
            
            def _health_check(self):
                return {
                    "workflow_ready": self.workflow is not None,
                    "workflow_steps": len(self.workflow.steps) if self.workflow else 0
                }
            
            async def execute_workflow(self, context=None):
                if not self.workflow:
                    return {"error": "Service not started"}
                return await self.workflow.execute_workflow(context)
        
        service = WorkflowService()
        
        # Test service health
        health = service.health_check()
        assert health["healthy"] is True
        assert health["data"]["workflow_ready"] is True
        assert health["data"]["workflow_steps"] == 2
        
        # Test workflow execution
        result = await service.execute_workflow({"test": "data"})
        assert result["success"] is True
        assert len(result["results"]) == 2