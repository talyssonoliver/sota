#!/usr/bin/env python3
"""
Base Test Classes

This module provides base test classes to eliminate duplication of
setup/teardown patterns across the test suite.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch

# Ensure proper import path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and teardown."""
    
    def setUp(self):
        """Set up common test environment."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Common test data
        self.test_data = {
            "task_id": "TEST-01",
            "agent_id": "test_agent",
            "timestamp": "2025-01-27T10:00:00Z"
        }
    
    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_temp_file(self, filename: str, content: str = "") -> Path:
        """Create a temporary file with content."""
        file_path = self.temp_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path
    
    def create_temp_json(self, filename: str, data: Dict[str, Any]) -> Path:
        """Create a temporary JSON file."""
        content = json.dumps(data, indent=2)
        return self.create_temp_file(filename, content)


class AgentTestCase(BaseTestCase):
    """Base test case for agent-related tests."""
    
    def setUp(self):
        """Set up agent test environment."""
        super().setUp()
        
        # Common agent test data
        self.agent_config = {
            "name": "Test Agent",
            "type": "test",
            "tools": ["echo", "file"],
            "memory": {"enabled": True}
        }
        
        self.mock_agent = Mock()
        self.mock_agent.execute.return_value = {
            "output": "Test execution completed",
            "task_id": self.test_data["task_id"],
            "agent_id": self.test_data["agent_id"]
        }
    
    def create_mock_agent_registry(self):
        """Create a mock agent registry."""
        return {
            "test_agent": self.mock_agent,
            "backend_engineer": Mock(),
            "frontend_engineer": Mock(),
            "qa": Mock()
        }


class WorkflowTestCase(BaseTestCase):
    """Base test case for workflow-related tests."""
    
    def setUp(self):
        """Set up workflow test environment."""
        super().setUp()
        
        # Common workflow test data
        self.workflow_config = {
            "name": "test_workflow",
            "steps": ["step1", "step2", "step3"],
            "parallel": False
        }
        
        self.task_declaration = {
            "id": self.test_data["task_id"],
            "title": "Test Task",
            "description": "Test task description",
            "owner": "test_agent",
            "state": "READY",
            "priority": "HIGH",
            "estimation_hours": 2.0,
            "depends_on": [],
            "artefacts": ["test.py"],
            "context_topics": ["testing"]
        }
    
    def create_task_directory(self, task_id: str = None) -> Path:
        """Create a task directory structure."""
        if task_id is None:
            task_id = self.test_data["task_id"]
        
        task_dir = self.temp_path / task_id
        task_dir.mkdir(exist_ok=True)
        
        # Create common task files
        declaration_file = task_dir / "task_declaration.json"
        declaration_file.write_text(json.dumps(self.task_declaration, indent=2))
        
        return task_dir


class MemoryTestCase(BaseTestCase):
    """Base test case for memory-related tests."""
    
    def setUp(self):
        """Set up memory test environment."""
        super().setUp()
        
        # Mock memory configuration
        self.memory_config = {
            "engine": "test",
            "embedding_model": "test-embeddings",
            "chunk_size": 1000,
            "chunk_overlap": 200
        }
        
        # Common test documents
        self.test_documents = [
            "This is a test document about API development.",
            "This document covers database schema design.",
            "Frontend component testing strategies."
        ]
    
    def create_mock_memory_engine(self):
        """Create a mock memory engine."""
        mock_engine = Mock()
        mock_engine.add_documents.return_value = True
        mock_engine.similarity_search.return_value = [
            {"content": doc, "score": 0.9} for doc in self.test_documents
        ]
        mock_engine.get_relevant_context.return_value = " ".join(self.test_documents)
        return mock_engine


class IntegrationTestCase(BaseTestCase):
    """Base test case for integration tests."""
    
    def setUp(self):
        """Set up integration test environment."""
        super().setUp()
        
        # Create mock project structure
        self.project_root = self.temp_path / "project"
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"
        self.config_dir = self.project_root / "config"
        
        for directory in [self.src_dir, self.tests_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def create_mock_environment(self):
        """Create a mock environment with common patches."""
        patches = {
            'os.environ': patch.dict(os.environ, {
                'TESTING': 'true',
                'PROJECT_ROOT': str(self.project_root)
            }),
            'pathlib.Path.cwd': patch('pathlib.Path.cwd', return_value=self.project_root)
        }
        return patches


class APITestCase(BaseTestCase):
    """Base test case for API-related tests."""
    
    def setUp(self):
        """Set up API test environment."""
        super().setUp()
        
        # Common API test data
        self.api_config = {
            "host": "localhost",
            "port": 8000,
            "debug": True
        }
        
        self.test_request = {
            "method": "POST",
            "path": "/api/test",
            "headers": {"Content-Type": "application/json"},
            "body": {"message": "test"}
        }
        
        self.test_response = {
            "status": 200,
            "data": {"result": "success"},
            "message": "Test completed"
        }


class DatabaseTestCase(BaseTestCase):
    """Base test case for database-related tests."""
    
    def setUp(self):
        """Set up database test environment."""
        super().setUp()
        
        # Mock database configuration
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user"
        }
        
        # Sample test data
        self.test_records = [
            {"id": 1, "name": "Test Record 1", "active": True},
            {"id": 2, "name": "Test Record 2", "active": False}
        ]
    
    def create_mock_database(self):
        """Create a mock database connection."""
        mock_db = Mock()
        mock_db.execute.return_value = self.test_records
        mock_db.fetch_all.return_value = self.test_records
        mock_db.fetch_one.return_value = self.test_records[0]
        return mock_db


class SecurityTestCase(BaseTestCase):
    """Base test case for security-related tests."""
    
    def setUp(self):
        """Set up security test environment."""
        super().setUp()
        
        # Common security test data
        self.malicious_inputs = [
            '<script>alert("xss")</script>',
            '../../../etc/passwd',
            'DROP TABLE users;',
            '{{}}.__class__.__bases__[0].__subclasses__()',
            '\x00\x01\x02',  # null bytes
            'A' * 10000,  # large input
        ]
        
        self.safe_inputs = [
            'normal text input',
            'user@example.com',
            '123-456-7890',
            'Valid Name'
        ]
    
    def assert_input_sanitized(self, input_value: str, result: Any):
        """Assert that input has been properly sanitized."""
        # Check that result doesn't contain the original malicious input
        result_str = str(result)
        self.assertNotIn('<script>', result_str.lower())
        self.assertNotIn('drop table', result_str.lower())
        self.assertNotIn('__class__', result_str)


# Utility functions for common test operations
def skip_if_no_dependency(dependency_name: str):
    """Decorator to skip tests if a dependency is not available."""
    def decorator(test_func):
        def wrapper(self):
            try:
                __import__(dependency_name)
            except ImportError:
                self.skipTest(f"Dependency {dependency_name} not available")
            return test_func(self)
        return wrapper
    return decorator


def mock_environment(**env_vars):
    """Decorator to mock environment variables for a test."""
    def decorator(test_func):
        def wrapper(self):
            with patch.dict(os.environ, env_vars):
                return test_func(self)
        return wrapper
    return decorator


def with_temp_directory(test_func):
    """Decorator to provide a temporary directory for a test."""
    def wrapper(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = temp_dir
            return test_func(self)
    return wrapper