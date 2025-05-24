"""
Test suite for MCP Context Integration with Agents - Complete Fix
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create comprehensive mocks for CrewAI I18N system
class MockI18N:
    def __init__(self):
        self.slices = {
            "observation": "\nObservation:",
            "task": "\nTask: {input}",
            "memory": "\nMemory: {memory}",
            "role_playing": "You are {role}",
            "tools": "\nTools: {tools}",
            "final_answer": "\nFinal Answer:",
            "no_tools": "No tools available."
        }
        self._prompts = {'slices': self.slices}
    
    def get(self, key, default=None):
        if key == 'no_tools':
            return 'No tools available.'
        return self.slices.get(key, default)
    
    def retrieve(self, kind, key):
        if key == 'no_tools':
            return 'No tools available.'
        return self._prompts.get(kind, {}).get(key, f"Missing: {key}")
    
    def slice(self, slice_name):
        if slice_name == 'no_tools':
            return 'No tools available.'
        return self.retrieve('slices', slice_name)

# Mock the Prompts class
class MockPrompts:
    def __init__(self):
        self.slices = {
            "observation": "\nObservation:",
            "task": "\nTask: {input}",
            "memory": "\nMemory: {memory}",
            "role_playing": "You are {role}",
            "tools": "\nTools: {tools}",
            "final_answer": "\nFinal Answer:",
            "no_tools": "No tools available."
        }
        self._prompts = {'slices': self.slices}
        
    def get(self, key, default=None):
        if key == 'no_tools':
            return 'No tools available.'
        return self.slices.get(key, default)
    
    def retrieve(self, kind, key):
        if key == 'no_tools':
            return 'No tools available.'
        return self._prompts.get(kind, {}).get(key, f"Missing: {key}")
    
    def slice(self, slice_name):
        if slice_name == 'no_tools':
            return 'No tools available.'
        return self.retrieve('slices', slice_name)

# Create a mock JSON file content that CrewAI expects
MOCK_TRANSLATION_JSON = {
    "hierarchical_manager_agent": {
        "role": "Manager",
        "goal": "Manage tasks efficiently",
        "backstory": "You are an experienced manager"
    },
    "slices": {
        "observation": "\nObservation:",
        "task": "\nTask: {input}",
        "memory": "\nMemory: {memory}",
        "role_playing": "You are {role}",
        "tools": "\nTools: {tools}",
        "final_answer": "\nFinal Answer:",
        "no_tools": "No tools available."
    }
}

# Mock file operations to prevent real file access
def mock_file_open(file_path, mode='r', **kwargs):
    # Handle WindowsPath or Path objects
    if hasattr(file_path, 'as_posix') or hasattr(file_path, 'as_uri'):
        file_path = str(file_path)
    # If binary mode or likely a tokenizer/encoding file, return bytes
    if 'b' in mode or any(file_path.endswith(ext) for ext in ['.tiktoken', '.bpe', '.model', '.bin', '.jsonl']):
        return mock_open(read_data=b"test: config").return_value
    if 'en.json' in file_path or 'prompts' in file_path:
        return mock_open(read_data=json.dumps(MOCK_TRANSLATION_JSON))()
    else:
        return mock_open(read_data="test: config")()

# Patch os.rename to a no-op to avoid FileNotFoundError from tiktoken atomic move
def noop_rename(src, dst):
    return None

# Apply all necessary patches before importing
with patch('os.rename', noop_rename):
    with patch('builtins.open', side_effect=mock_file_open):
        with patch('json.load', return_value=MOCK_TRANSLATION_JSON):
            with patch('crewai.utilities.i18n.I18N', MockI18N):
                with patch('crewai.utilities.prompts.Prompts', MockPrompts):
                    from agents import agent_builder
                    from agents.backend import build_backend_agent, get_backend_context
                    from agents.frontend import build_frontend_agent, get_frontend_context
                    from agents.technical import build_technical_agent, get_technical_context
                    from agents.qa import build_qa_agent, get_qa_context
                    from agents.doc import build_doc_agent, get_doc_context
                    from agents.coordinator import build_coordinator_agent, get_coordinator_context
                    from orchestration.inject_context import context_injector

class TestMemoryIntegration(unittest.TestCase):
    """Test MCP context integration with agents"""
    
    def setUp(self):
        self.task_metadata = {
            "id": "BE-07",
            "title": "Implement Service Functions",
            "description": "Create Supabase service layer functions",
            "context_topics": ["db-schema", "service-patterns"],
            "owner": "backend_engineer",
            "assigned_agent": "backend_engineer",
            "labels": ["api", "database"],
            "priority": "high"
        }
        
        self.mock_context = [
            "Database schema for user management",
            "Service layer patterns for CRUD operations",
            "Best practices for error handling"
        ]

    @patch('builtins.open', side_effect=mock_file_open)
    @patch('json.load', return_value=MOCK_TRANSLATION_JSON)
    @patch('crewai.utilities.i18n.I18N', MockI18N)
    @patch('crewai.utilities.prompts.Prompts', MockPrompts)
    @patch('agents.agent_builder.memory')
    def test_agent_builder_initialization(self, mock_memory, *args):
        """Test that agent builder initializes correctly"""
        mock_memory.get_context_by_domains.return_value = self.mock_context
        mock_memory.get_retriever.return_value = MagicMock()
        
        builder = agent_builder.MemoryEnabledAgentBuilder()
        self.assertIsNotNone(builder)
        self.assertIsNotNone(builder.memory)

    @patch('builtins.open', side_effect=mock_file_open)
    @patch('json.load', return_value=MOCK_TRANSLATION_JSON)
    @patch('crewai.utilities.i18n.I18N', MockI18N)
    @patch('crewai.utilities.prompts.Prompts', MockPrompts)
    @patch('agents.agent_builder.memory')
    def test_build_backend_agent_with_context(self, mock_memory, *args):
        """Test building backend agent with context"""
        mock_memory.get_context_by_domains.return_value = self.mock_context
        mock_memory.get_retriever.return_value = MagicMock()
        
        # Mock the config file loading
        with patch('yaml.safe_load', return_value={"backend_engineer": {"name": "Backend Agent"}}):
            agent = build_backend_agent(task_metadata=self.task_metadata)
            self.assertIsNotNone(agent)

    @patch('builtins.open', side_effect=mock_file_open)
    @patch('json.load', return_value=MOCK_TRANSLATION_JSON)
    @patch('crewai.utilities.i18n.I18N', MockI18N)
    @patch('crewai.utilities.prompts.Prompts', MockPrompts)
    @patch('agents.agent_builder.memory')
    def test_context_retrieval_for_backend_agent(self, mock_memory, *args):
        """Test context retrieval for backend agent"""
        mock_memory.get_context_by_domains.return_value = self.mock_context
        
        context = get_backend_context(self.task_metadata)
        self.assertIsNotNone(context)
        mock_memory.get_context_by_domains.assert_called_once()

    @patch('builtins.open', side_effect=mock_file_open)
    @patch('json.load', return_value=MOCK_TRANSLATION_JSON)
    @patch('crewai.utilities.i18n.I18N', MockI18N)
    @patch('crewai.utilities.prompts.Prompts', MockPrompts)
    @patch('agents.agent_builder.memory')
    def test_get_frontend_context(self, mock_memory, *args):
        """Test frontend context retrieval"""
        mock_memory.get_context_by_domains.return_value = ["UI patterns", "Component library"]
        
        context = get_frontend_context(self.task_metadata)
        self.assertIsNotNone(context)

    @patch('builtins.open', side_effect=mock_file_open)
    @patch('json.load', return_value=MOCK_TRANSLATION_JSON)
    @patch('crewai.utilities.i18n.I18N', MockI18N)
    @patch('crewai.utilities.prompts.Prompts', MockPrompts)
    @patch('agents.agent_builder.memory')
    def test_get_backend_context(self, mock_memory, *args):
        """Test backend context retrieval"""
        mock_memory.get_context_by_domains.return_value = self.mock_context
        
        context = get_backend_context(self.task_metadata)
        self.assertIsNotNone(context)

    @patch('builtins.open', side_effect=mock_file_open)
    @patch('json.load', return_value=MOCK_TRANSLATION_JSON)
    @patch('crewai.utilities.i18n.I18N', MockI18N)
    @patch('crewai.utilities.prompts.Prompts', MockPrompts)
    @patch('agents.agent_builder.memory')
    def test_context_enhancement_prompt(self, mock_memory, *args):
        """Test prompt enhancement with context"""
        mock_memory.get_context_by_domains.return_value = self.mock_context
        
        builder = agent_builder.MemoryEnabledAgentBuilder()
        enhanced_prompt = builder._enhance_prompt_with_context(
            "Create a service function", 
            self.mock_context
        )
        
        self.assertIn("Create a service function", enhanced_prompt)
        self.assertIn("Database schema", enhanced_prompt)

    @patch('builtins.open', side_effect=mock_file_open)
    @patch('json.load', return_value=MOCK_TRANSLATION_JSON)
    @patch('crewai.utilities.i18n.I18N', MockI18N)
    @patch('crewai.utilities.prompts.Prompts', MockPrompts)
    @patch('agents.agent_builder.memory')
    def test_context_error_handling(self, mock_memory, *args):
        """Test graceful handling of context retrieval errors"""
        import os
        old_testing = os.environ.get("TESTING")
        os.environ["TESTING"] = "1"
        try:
            mock_memory.get_context_by_domains.side_effect = Exception("Memory error")
            # Should not raise an exception
            context = get_backend_context(self.task_metadata)
            self.assertIsNone(context)
        finally:
            if old_testing is not None:
                os.environ["TESTING"] = old_testing
            else:
                del os.environ["TESTING"]

    @patch('builtins.open', side_effect=mock_file_open)
    @patch('json.load', return_value=MOCK_TRANSLATION_JSON)
    @patch('crewai.utilities.i18n.I18N', MockI18N)
    @patch('crewai.utilities.prompts.Prompts', MockPrompts)
    @patch('agents.agent_builder.memory')
    def test_context_injection_for_different_roles(self, mock_memory, *args):
        """Test context injection works for different agent roles"""
        mock_memory.get_context_by_domains.return_value = "Role-specific context"
        mock_memory.get_retriever.return_value = MagicMock()
        
        # Test different roles
        roles = ["backend_engineer", "frontend_engineer", "technical_lead", "qa", "doc"]
        with patch('yaml.safe_load', return_value={}):
            for role in roles:
                with self.subTest(role=role):
                    agent = agent_builder.build_agent(role=role, task_metadata=self.task_metadata)
                    self.assertIsNotNone(agent)

    @patch('builtins.open', side_effect=mock_file_open)
    @patch('json.load', return_value=MOCK_TRANSLATION_JSON)
    @patch('crewai.utilities.i18n.I18N', MockI18N)
    @patch('crewai.utilities.prompts.Prompts', MockPrompts)
    @patch('agents.agent_builder.memory')
    def test_role_context_mapping(self, mock_memory, *args):
        """Test that role context mapping works correctly"""
        builder = agent_builder.MemoryEnabledAgentBuilder()
        
        # Test backend role mapping
        domains = builder._get_context_domains_for_role("backend_engineer")
        self.assertIn("db-schema", domains)
        self.assertIn("service-patterns", domains)
        
        # Test frontend role mapping
        domains = builder._get_context_domains_for_role("frontend_engineer")
        self.assertIn("design-system", domains)
        self.assertIn("ui-patterns", domains)

    @patch('builtins.open', side_effect=mock_file_open)
    @patch('json.load', return_value=MOCK_TRANSLATION_JSON)
    @patch('crewai.utilities.i18n.I18N', MockI18N)
    @patch('crewai.utilities.prompts.Prompts', MockPrompts)
    @patch('agents.agent_builder.memory')
    def test_context_injector_prepare_agent(self, mock_memory, *args):
        """Test context injector preparing agent with context"""
        mock_memory.get_context_by_domains.return_value = self.mock_context
        mock_memory.get_retriever.return_value = MagicMock()
        
        # Mock task metadata loading
        with patch('utils.task_loader.load_task_metadata', return_value=self.task_metadata):
            with patch('yaml.safe_load', return_value={}):
                agent = context_injector.prepare_agent_with_context("BE-07", "backend_engineer")
                self.assertIsNotNone(agent)

    @patch('builtins.open', side_effect=mock_file_open)
    @patch('json.load', return_value=MOCK_TRANSLATION_JSON)
    @patch('crewai.utilities.i18n.I18N', MockI18N)
    @patch('crewai.utilities.prompts.Prompts', MockPrompts)
    def test_generic_prompt_generation(self, *args):
        """Test generic prompt generation utilities"""
        from prompts.utils import load_generic_prompt, format_prompt_with_context
        
        prompt = load_generic_prompt("test_template")
        self.assertIsNotNone(prompt)
        
        formatted = format_prompt_with_context(
            "Base prompt: {context}",
            self.mock_context
        )
        self.assertIn("Database schema", formatted)


class TestContextFormats(unittest.TestCase):
    """Test context format handling"""
    
    def setUp(self):
        self.context = [
            "Database schema for user management",
            "Service layer patterns for CRUD operations",
            "Source: database, file, api."
        ]
    
    @patch('builtins.open', side_effect=mock_file_open)
    @patch('json.load', return_value=MOCK_TRANSLATION_JSON)
    @patch('crewai.utilities.i18n.I18N', MockI18N)
    @patch('crewai.utilities.prompts.Prompts', MockPrompts)
    def test_context_logging_structure(self, *args):
        """Test context logging maintains proper structure"""
        from orchestration.execute_task import extract_context_sources
        
        sources = extract_context_sources(self.context)
        self.assertIsInstance(sources, list)
        self.assertTrue(len(sources) > 0)

    @patch('builtins.open', side_effect=mock_file_open)
    @patch('json.load', return_value=MOCK_TRANSLATION_JSON)
    @patch('crewai.utilities.i18n.I18N', MockI18N)
    @patch('crewai.utilities.prompts.Prompts', MockPrompts)
    def test_context_source_extraction(self, *args):
        """Test context source extraction utility"""
        from orchestration.execute_task import extract_context_sources
        
        sources = extract_context_sources(self.context)
        self.assertIn("database", sources[0].lower())


if __name__ == '__main__':
    unittest.main()
