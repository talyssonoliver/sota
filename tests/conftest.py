import logging
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ===========================
# PERFORMANCE OPTIMIZATIONS
# ===========================


@pytest.fixture(autouse=True)
def fast_test_environment(tmp_path, monkeypatch):
    """Auto-mock external services and create isolated environment for all tests"""

    # Start performance tracking
    start_time = time.time()

    # 1. Mock External Services (Phase 1: Quick Wins)
    with patch('langsmith.client.Client') as mock_langsmith, \
            patch('requests.post') as mock_slack, \
            patch('httpx.post') as mock_httpx, \
            patch('chromadb.Client') as mock_chromadb:

        # Configure external service mocks
        mock_langsmith.return_value.multipart_ingest.return_value = {
            "success": True}
        mock_slack.return_value.status_code = 200
        mock_httpx.return_value.status_code = 200
        mock_chromadb.return_value.get_or_create_collection.return_value = MagicMock()

        # 2. Environment Isolation (Phase 2: Structure)
        monkeypatch.setenv("TEST_MODE", "true")
        monkeypatch.setenv("TESTING", "1")
        monkeypatch.setenv("TASK_DIR", str(tmp_path / "tasks"))
        monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "outputs"))
        monkeypatch.setenv("CONTEXT_STORE_DIR",
                           str(tmp_path / "context-store"))

        # Mock external config
        monkeypatch.setenv("SLACK_WEBHOOK_URL",
                           "http://mock-slack.com/webhook")
        monkeypatch.setenv("LANGSMITH_API_KEY", "mock-key")
        monkeypatch.setenv("ANONYMIZED_TELEMETRY", "False")

        # 3. Create Required Test Directories (Phase 2: Structure)
        test_dirs = [
            tmp_path / "tasks",
            tmp_path / "outputs",
            tmp_path / "context-store",
            tmp_path / "logs",
            tmp_path / "reports"
        ]
        for test_dir in test_dirs:
            test_dir.mkdir(parents=True, exist_ok=True)

        # 4. Create Test Task Metadata (Phase 1: Quick Wins)
        task_file = tmp_path / "tasks" / "BE-07.yaml"
        task_file.write_text("""
task_id: BE-07
title: Test Backend Task
agent_id: backend_engineer
description: Create service layer for orders and customers using Supabase
context_topics:
  - db-schema
  - service-layer-pattern
priority: HIGH
estimation_hours: 3
state: IN_PROGRESS
dependencies:
  - TL-09
  - BE-01
artefacts:
  - backend_service.py
  - api_endpoints.py
""".strip())

        yield

        # Performance tracking (Phase 3: Optimization)
        duration = time.time() - start_time
        if duration > 5.0:  # Log slow tests
            print(f"SLOW TEST SETUP: {duration:.2f}s")


@pytest.fixture(autouse=True)
def set_log_level():
    """Configure logging for clean test output"""
    logging.getLogger().setLevel(logging.WARNING)

    # Silence noisy loggers (Phase 1: Quick Wins)
    noisy_loggers = [
        "dotenv.main", "httpx", "chromadb", "MemoryEngine",
        "langsmith", "requests", "urllib3", "openai"
    ]
    for name in noisy_loggers:
        logging.getLogger(name).setLevel(logging.ERROR)

    # Patch print to silence output in test mode
    import builtins
    if os.environ.get("TESTING", "0") == "1":
        builtins.print = lambda *a, **k: None

# ===========================
# TEST DATA FIXTURES
# ===========================


@pytest.fixture
def valid_task_metadata():
    """Consistent task metadata for tests"""
    return {
        "task_id": "BE-07",
        "title": "Test Backend Task",
        "description": "Test description for backend service layer",
        "agent_id": "backend_engineer",
        "context_topics": ["db-schema", "service-layer-pattern"],
        "priority": "HIGH",
        "estimation_hours": 3,
        "state": "IN_PROGRESS",
        "artefacts": ["backend_service.py", "api_endpoints.py"]
    }


@pytest.fixture
def mock_memory_engine():
    """Mock memory engine with consistent behavior"""
    engine = MagicMock()
    engine._add_secure_embeddings = MagicMock(return_value=True)
    engine.get_context = MagicMock(return_value="test context")
    engine.search = MagicMock(return_value=[
        {"content": "Test context 1", "metadata": {"type": "test"}},
        {"content": "Test context 2", "metadata": {"type": "test"}}
    ])
    return engine


@pytest.fixture
def mock_vector_store():
    """Mock vector store operations"""
    store = MagicMock()
    store.add_documents = MagicMock(return_value=["doc1", "doc2"])
    store.similarity_search = MagicMock(return_value=[])
    return store

# ===========================
# RECURSION FIXES
# ===========================


@pytest.fixture
def workflow_recursion_limit():
    """Set safe recursion limits for workflow tests"""
    return 5  # Lower limit for tests

# ===========================
# PERFORMANCE MONITORING
# ===========================


@pytest.fixture(autouse=True)
def track_test_performance(request):
    """Track test performance and identify slow tests"""
    start_time = time.time()
    yield
    duration = time.time() - start_time

    if duration > 5.0:  # Log slow tests
        print(f"SLOW TEST: {request.node.name} took {duration:.2f}s")

# ===========================
# ENHANCED MOCKING & RECURSION FIXES
# ===========================


@pytest.fixture
def enhanced_workflow():
    """Enhanced workflow with recursion protection"""
    class EnhancedWorkflow:
        def __init__(self, max_iterations=5):  # Lower for tests
            self.max_iterations = max_iterations
            self.iteration_count = 0

        def execute_task(self, task_id):
            if self.iteration_count >= self.max_iterations:
                raise Exception(
                    f"Task {task_id} exceeded {self.max_iterations} iterations"
                )
            self.iteration_count += 1
            return {"status": "completed", "task_id": task_id}

    return EnhancedWorkflow()


@pytest.fixture
def mock_external_apis():
    """Comprehensive external API mocking"""
    with patch('openai.ChatCompletion.create') as mock_openai, \
            patch('crewai.Agent') as mock_agent, \
            patch('langgraph.graph.StateGraph') as mock_graph, \
            patch('supabase.create_client') as mock_supabase:

        # Configure mocks
        mock_openai.return_value = {
            "choices": [{"message": {"content": "Mock response"}}]
        }
        mock_agent.return_value = MagicMock()
        mock_graph.return_value = MagicMock()
        mock_supabase.return_value = MagicMock()

        yield {
            "openai": mock_openai,
            "crewai": mock_agent,
            "langgraph": mock_graph,
            "supabase": mock_supabase
        }


@pytest.fixture(scope="session")
def test_performance_tracker():
    """Track test performance across the session"""
    class PerformanceTracker:
        def __init__(self):
            self.slow_tests = []
            self.total_tests = 0
            self.total_time = 0

        def record_test(self, test_name, duration):
            self.total_tests += 1
            self.total_time += duration
            if duration > 3.0:  # Tests taking >3s are considered slow
                self.slow_tests.append((test_name, duration))

        def get_summary(self):
            avg_time = self.total_time / max(self.total_tests, 1)
            return {
                "total_tests": self.total_tests,
                "total_time": self.total_time,
                "average_time": avg_time,
                "slow_tests": self.slow_tests
            }

    tracker = PerformanceTracker()
    yield tracker

    # Print summary at end of session
    summary = tracker.get_summary()
    if summary["slow_tests"]:
        print(
            f"\n⚠️  SLOW TESTS DETECTED ({len(summary['slow_tests'])} tests):")
        for test_name, duration in summary["slow_tests"]:
            print(f"   • {test_name}: {duration:.2f}s")

# ===========================
# MEMORY ENGINE ENHANCEMENTS
# ===========================


@pytest.fixture
def enhanced_memory_engine():
    """Enhanced memory engine mock with missing methods"""
    class MockMemoryEngine:
        def __init__(self):
            self.documents = []
            self.embeddings = {}

        def _add_secure_embeddings(self, texts, metadata=None):
            """Mock secure embeddings addition"""
            for i, text in enumerate(texts):
                self.embeddings[f"doc_{i}"] = {
                    "text": text,
                    "metadata": metadata[i] if metadata else {}
                }
            return True

        def get_context(self, query, limit=5):
            """Mock context retrieval"""
            return f"Mock context for: {query}"

        def search(self, query, limit=5):
            """Mock search functionality"""
            return [
                {"content": f"Result 1 for {query}", "score": 0.9},
                {"content": f"Result 2 for {query}", "score": 0.8}
            ]

        def build_focused_context(self, topics, max_tokens=1000):
            """Mock focused context building"""
            return f"Focused context for topics: {', '.join(topics)}"

        def get_documents(self, filters=None):
            """Mock document retrieval"""
            return self.documents

    return MockMemoryEngine()

# ===========================
# ENHANCED WORKFLOW MOCKING
# ===========================


@pytest.fixture
def mock_workflow_execution():
    """Mock workflow execution to prevent recursion"""
    def safe_workflow_execute(*args, **kwargs):
        # Simulate a successful workflow execution without actual recursion
        return {
            'result': 'Mock workflow completed',
            'status': 'success',
            'execution_duration': 0.1,
            'enhanced_prompt': 'You are a test agent. Task completed successfully.',
            'metadata': {
                'test': True}}

    with patch('orchestration.execute_graph.run_task_graph', side_effect=safe_workflow_execute) as mock_run_graph, \
            patch('orchestration.execute_graph.build_task_state') as mock_build_state, \
            patch('orchestration.execute_graph.build_advanced_workflow_graph') as mock_build_workflow, \
            patch('orchestration.execute_graph.load_task_metadata') as mock_load_metadata:

        # Configure task state builder to return proper structure
        mock_build_state.return_value = {
            'task_id': 'BE-07',
            'title': 'Backend Service Layer Implementation',
            'description': 'Create service layer for orders and customers using Supabase',
            'enhanced_prompt': 'Test prompt',
            'status': 'ready',
            'context': 'Test context',
            'dependencies': [
                'TL-09',
                'BE-01'],
            'priority': 'HIGH',
            'estimation_hours': 3,
            'artefacts': [
                'backend_service.py',
                'api_endpoints.py']}

        # Configure metadata loader
        mock_load_metadata.return_value = {
            'task_id': 'BE-07',
            'title': 'Backend Service Layer Implementation',
            'description': 'Create service layer for orders and customers using Supabase',
            'priority': 'HIGH',
            'estimation_hours': 3,
            'state': 'FAILED',
            'context_topics': [
                'db-schema',
                'service-layer-pattern'],
            'artefacts': [
                'backend_service.py',
                'api_endpoints.py']}

        # Configure graph runner with controlled execution
        mock_run_graph.return_value = {
            'result': 'Mock execution complete',
            'status': 'success',
            'execution_duration': 0.1
        }

        yield {
            'execute_workflow': safe_workflow_execute,
            'build_task_state': mock_build_state,
            'run_task_graph': mock_run_graph,
            'build_workflow': mock_build_workflow,
            'load_metadata': mock_load_metadata
        }

# ===========================
# PHASE 2 OPTIMIZATIONS: MAKING SLOW TESTS FAST
# ===========================


@pytest.fixture
def fast_notification_config():
    """Speed up notification tests by mocking delays and external calls."""
    with patch('time.sleep'), \
            patch('requests.post') as mock_post, \
            patch('asyncio.sleep'), \
            patch('graph.notifications.send_notification') as mock_notify, \
            patch('graph.notifications.NotificationManager.send') as mock_send:

        mock_post.return_value.status_code = 200
        mock_notify.return_value = {
            "success": True, "sent_at": "2025-05-26T10:00:00Z"}
        mock_send.return_value = True
        yield


@pytest.fixture
def fast_retry_config():
    """Minimal retry configuration for tests - reduces 10s+ to <1s."""
    return {
        'max_retries': 1,        # vs production: 5-10
        'retry_delay': 0,        # vs production: 1.0s
        'backoff_factor': 1,     # vs production: 2
        'timeout': 1             # vs production: 30s
    }


@pytest.fixture
def mock_graph_execution():
    """Mock heavy graph operations for fast testing."""
    with patch('langgraph.graph.StateGraph.compile') as mock_compile, \
            patch('langgraph.graph.CompiledGraph.invoke') as mock_invoke, \
            patch('orchestration.execute_graph.build_task_state') as mock_build_state:

        # Mock compiled graph
        mock_compiled_graph = MagicMock()
        mock_compile.return_value = mock_compiled_graph

        # Mock graph invocation with immediate success
        mock_invoke.return_value = {
            "task_id": "TEST-01",
            "status": "COMPLETED",
            "result": "mock_result",
            "execution_time": 0.001,
            "agent": "test_agent",
            "output": "Mock task completed successfully"
        }

        # Mock state building
        mock_build_state.return_value = {
            "task_id": "TEST-01",
            "title": "Test Task",
            "status": "IN_PROGRESS",
            "dependencies": [],
            "context": "Mock context",
            "metadata": {}
        }

        yield {
            'compile': mock_compile,
            'invoke': mock_invoke,
            'build_state': mock_build_state
        }


@pytest.fixture(scope="session")
def mock_vector_store():
    """Session-scoped mock vector store to avoid repeated setup."""
    store = MagicMock()

    # Pre-computed responses for common queries
    store.similarity_search.return_value = [
        {"content": "mock document 1", "metadata": {
            "score": 0.9, "source": "test"}},
        {"content": "mock document 2", "metadata": {"score": 0.8, "source": "test"}}
    ]

    store.add_documents.return_value = ["doc1", "doc2"]
    store.get_collection.return_value = MagicMock()
    store.delete_collection.return_value = True

    return store


@pytest.fixture
def fast_memory_engine(mock_vector_store):
    """Fast memory engine with mocked operations."""
    with patch('memory_engine.MemoryEngine._initialize_vector_store', return_value=mock_vector_store), \
            patch('memory_engine.MemoryEngine._add_secure_embeddings', return_value=True), \
            patch('chromadb.Client') as mock_client, \
            patch('memory_engine.MemoryEngine.get_context') as mock_get_context:

        mock_client.return_value = MagicMock()
        mock_get_context.return_value = {
            "relevant_docs": ["doc1", "doc2"],
            "context": "Mock context for fast testing",
            "metadata": {"source": "mock", "confidence": 0.9}
        }
        yield mock_vector_store


@pytest.fixture
def mock_workflow_execution():
    """Mock the entire workflow execution pipeline for speed."""
    with patch('orchestration.enhanced_workflow.EnhancedWorkflowExecutor._build_workflow') as mock_build, \
            patch('orchestration.enhanced_workflow.EnhancedWorkflowExecutor.check_dependencies') as mock_deps:

        mock_workflow = MagicMock()
        mock_workflow.invoke.return_value = {
            "task_id": "TEST-01",
            "status": "COMPLETED",
            "agent": "test_agent",
            "output": "Mock workflow execution completed",
            "timestamp": "2025-05-26T10:00:00Z"
        }
        mock_build.return_value = mock_workflow
        mock_deps.return_value = (True, "All dependencies satisfied")

        yield {
            'build': mock_build,
            'workflow': mock_workflow,
            'dependencies': mock_deps
        }


@pytest.fixture
def performance_tracker():
    """Track test performance and fail if too slow."""
    start_time = time.time()
    yield
    duration = time.time() - start_time

    # Fail test if it takes longer than expected (configurable)
    max_duration = float(os.environ.get('MAX_TEST_DURATION', '5.0'))
    if duration > max_duration:
        pytest.fail(f"Test took {duration:.2f}s, max allowed: {max_duration}s")


@pytest.fixture
def mock_crewai_agents():
    """Mock CrewAI agents to avoid heavy initialization."""
    with patch('crewai.Agent') as mock_agent_class, \
            patch('crewai.Crew') as mock_crew_class:

        mock_agent = MagicMock()
        mock_agent.execute.return_value = {
            "output": "Mock agent execution result",
            "status": "completed"
        }
        mock_agent_class.return_value = mock_agent

        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = {
            "final_output": "Mock crew execution result",
            "tasks_outputs": []
        }
        mock_crew_class.return_value = mock_crew

        yield {
            'agent': mock_agent,
            'crew': mock_crew,
            'agent_class': mock_agent_class,
            'crew_class': mock_crew_class
        }


# =============================================================================
# CONDITIONAL TEST EXECUTION
# =============================================================================

def should_run_expensive_test():
    """Only run expensive tests when necessary."""
    return os.environ.get('RUN_EXPENSIVE_TESTS', 'false').lower() == 'true'


def should_run_integration_test():
    """Only run integration tests when requested."""
    return os.environ.get('RUN_INTEGRATION_TESTS', 'true').lower() == 'true'


# =============================================================================
# PYTEST MARKERS AND CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line(
        "markers",
        "expensive: marks tests as expensive (requires RUN_EXPENSIVE_TESTS=true)")
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "fast: marks tests as fast/optimized")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle markers."""
    for item in items:
        # Auto-mark slow tests based on common patterns
        if any(
            pattern in item.name for pattern in [
                'notification_integration',
                'resilient_workflow',
                'memory_integration']):
            item.add_marker(pytest.mark.slow)

        # Auto-mark expensive tests
        if 'expensive' in item.name or should_run_expensive_test():
            item.add_marker(pytest.mark.expensive)
