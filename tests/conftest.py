# pylint: disable=redefined-outer-name
"""
Pytest configuration/fixtures para ai-system.

• Isolamento de ambiente e mocks pesados
• Auto-marcação de testes por tempo (unit / integration / slow)
• Otimizações de desempenho para CI
"""

from __future__ import annotations

import builtins
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Generator, List
from unittest.mock import MagicMock, patch

import pytest

# ──────────────────────────────────────────────────────────────────────────────
#  CONSTANTES – AUTO-MARCAÇÃO POR DURAÇÃO
# ──────────────────────────────────────────────────────────────────────────────
_DURATION_CACHE = Path(".pytest_durations.json")
_THRESHOLDS = {"unit": 1.0, "integration": 5.0}  # seg

# ──────────────────────────────────────────────────────────────────────────────
#  EXCEPTIONS ESPECÍFICAS
# ──────────────────────────────────────────────────────────────────────────────
class RecursionLimitExceededError(RuntimeError):
    """Estouro intencional de recursão em testes."""


# ──────────────────────────────────────────────────────────────────────────────
#  FIXTURES GLOBAIS (auto-use)
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def fast_test_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Mocka serviços externos + cria diretórios temporários."""
    start = time.perf_counter()

    # Network isolation to prevent accidental external calls
    import socket
    original_getaddrinfo = socket.getaddrinfo
    socket.getaddrinfo = lambda *args: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 80))]

    with patch("langsmith.client.Client"), \
         patch("requests.post") as mock_slack, \
         patch("httpx.post") as mock_httpx, \
         patch("chromadb.Client"), \
         patch("langchain_openai.ChatOpenAI"):

        mock_slack.return_value.status_code = 200
        mock_httpx.return_value.status_code = 200

        # ENV
        monkeypatch.setenv("TEST_MODE", "true")
        monkeypatch.setenv("TESTING", "1")
        monkeypatch.setenv("TASK_DIR", str(tmp_path / "tasks"))
        monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "outputs"))
        monkeypatch.setenv("CONTEXT_STORE_DIR", str(tmp_path / "context-store"))
        monkeypatch.setenv("SLACK_WEBHOOK_URL", "http://mock-slack.com/webhook")
        monkeypatch.setenv("LANGSMITH_API_KEY", "mock-key")
        monkeypatch.setenv("OPENAI_API_KEY", "mock-openai-key")
        monkeypatch.setenv("ANONYMIZED_TELEMETRY", "False")
        monkeypatch.setenv("DISABLE_WORKFLOW_MONITORING", "1")

        # diretórios
        for d in (
            tmp_path / "tasks",
            tmp_path / "outputs",
            tmp_path / "context-store",
            tmp_path / "logs",
            tmp_path / "reports",
        ):
            d.mkdir(parents=True, exist_ok=True)

        # task YAML mínima
        (tmp_path / "tasks" / "BE-07.yaml").write_text(
            "task_id: BE-07\ntitle: Test Backend Task\nstate: IN_PROGRESS\n"
        )

        yield

    # Restore network
    socket.getaddrinfo = original_getaddrinfo
    
    # log de setups lentos (>2 s)
    elapsed = time.perf_counter() - start
    if elapsed > 2:
        print(f"SLOW GLOBAL SETUP: {elapsed:.2f}s")


@pytest.fixture(autouse=True)
def set_log_level() -> None:
    """Silencia logs ruidosos."""
    logging.getLogger().setLevel(logging.WARNING)
    noisy = ("dotenv.main", "httpx", "chromadb", "langsmith", "urllib3", "openai")
    for n in noisy:
        logging.getLogger(n).setLevel(logging.ERROR)

    if os.environ.get("TESTING") == "1":
        builtins.print = lambda *a, **k: None  # type: ignore[assignment]


# ──────────────────────────────────────────────────────────────────────────────
#  FIXTURES DE DADOS / UTILITÁRIOS
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def valid_task_metadata() -> Dict[str, Any]:
    return {
        "task_id": "BE-07",
        "title": "Test Backend Task",
        "description": "Test description",
        "agent_id": "backend_engineer",
        "priority": "HIGH",
        "state": "IN_PROGRESS",
    }


@pytest.fixture
def mock_memory_engine() -> MagicMock:
    engine = MagicMock()
    engine._add_secure_embeddings.return_value = True
    engine.get_context.return_value = "test context"
    engine.search.return_value = [{"content": "ctx", "metadata": {}}]
    return engine


# ──────────────────────────────────────────────────────────────────────────────
#  SESSION-SCOPED HEAVY FIXTURES (Performance Optimization)
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def mock_vector_store() -> MagicMock:
    store = MagicMock()
    store.similarity_search.return_value = []
    store.add_documents.return_value = ["doc1", "doc2"]
    return store

@pytest.fixture(scope="session")
def session_chromadb_client() -> Generator[MagicMock, None, None]:
    """Single ChromaDB client for entire test session."""
    with patch("chromadb.Client") as mock_client:
        client = MagicMock()
        client.get_or_create_collection.return_value = MagicMock()
        mock_client.return_value = client
        yield client

@pytest.fixture(scope="session")
def session_openai_client() -> Generator[MagicMock, None, None]:
    """Single OpenAI client mock for entire session."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        client = MagicMock()
        client.invoke.return_value = MagicMock(content="mock response")
        mock_openai.return_value = client
        yield client

@pytest.fixture(scope="session")
def session_supabase_client() -> Generator[MagicMock, None, None]:
    """Single Supabase client for entire session."""
    with patch("supabase.create_client") as mock_supabase:
        client = MagicMock()
        mock_supabase.return_value = client
        yield client


# ──────────────────────────────────────────────────────────────────────────────
#  LIMITES DE RECURSÃO / PERFORMANCE
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def workflow_recursion_limit() -> int:
    """Limite baixo de recursão p/ testes."""
    return 5


@pytest.fixture(autouse=True)
def track_test_performance(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    start = time.perf_counter()
    yield
    duration = time.perf_counter() - start
    if duration > 5:
        print(f"SLOW TEST: {request.node.nodeid} – {duration:.2f}s")


# ---------------------------------------------------------------------------- #
#  ENHANCED WORKFLOW & EXTERNAL APIS
# ---------------------------------------------------------------------------- #
@pytest.fixture
def enhanced_workflow() -> Any:
    class EnhancedWorkflow:
        def __init__(self, max_iterations: int = 5):
            self.max_iterations = max_iterations
            self.iteration_count = 0

        def execute_task(self, task_id: str) -> Dict[str, str]:
            if self.iteration_count >= self.max_iterations:
                raise RecursionLimitExceededError(task_id)
            self.iteration_count += 1
            return {"status": "completed", "task_id": task_id}

    return EnhancedWorkflow()


@pytest.fixture
def mock_external_apis() -> Generator[Dict[str, MagicMock], None, None]:
    with patch("openai.ChatCompletion.create") as p_openai, \
         patch("crewai.Agent") as p_agent, \
         patch("langgraph.graph.StateGraph") as p_graph, \
         patch("supabase.create_client") as p_supabase:

        yield {
            "openai": p_openai,
            "agent": p_agent,
            "graph": p_graph,
            "supabase": p_supabase,
        }


# ---------------------------------------------------------------------------- #
#  PERFORMANCE TRACKER (session)
# ---------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def test_performance_tracker() -> Generator[Any, None, None]:
    class Tracker:
        slow: List[tuple[str, float]] = []
        total: int = 0
        total_time: float = 0.0

        def record(self, name: str, dur: float) -> None:
            self.total += 1
            self.total_time += dur
            if dur > 3:
                self.slow.append((name, dur))

        def summary(self) -> Dict[str, Any]:
            return {
                "total": self.total,
                "avg": self.total_time / max(self.total, 1),
                "slow": self.slow,
            }

    t = Tracker()
    yield t
    if t.slow:
        print(f"\n⚠️  SLOW TESTS ({len(t.slow)}):")
        for n, d in t.slow:
            print(f"• {n}: {d:.2f}s")


# ---------------------------------------------------------------------------- #
#  ENHANCED MEMORY ENGINE
# ---------------------------------------------------------------------------- #
@pytest.fixture
def enhanced_memory_engine() -> Any:
    class MockMemoryEngine:
        documents: List[str] = []
        embeddings: Dict[str, Any] = {}

        def _add_secure_embeddings(self, texts, metadata=None):
            for i, txt in enumerate(texts):
                self.embeddings[f"doc_{i}"] = {"text": txt, "metadata": metadata or {}}
            return True

        def get_context(self, query, limit=5):
            return f"Mock context: {query}"

        def search(self, query, limit=5):
            return [{"content": f"Result {i}", "score": 1 - i * 0.1} for i in range(2)]

    return MockMemoryEngine()


# ---------------------------------------------------------------------------- #
#  WORKFLOW EXECUTION MOCK (única definição)
# ---------------------------------------------------------------------------- #
@pytest.fixture
def mock_workflow_execution() -> Generator[Dict[str, Any], None, None]:
    def _safe_execute(*_, **__) -> Dict[str, Any]:
        return {"status": "success", "result": "mock", "exec_time": 0.01}

    with patch("orchestration.execute_graph.run_task_graph", _safe_execute) as p_run, \
         patch("orchestration.execute_graph.build_task_state") as p_state:

        p_state.return_value = {"task_id": "BE-07", "status": "READY"}
        yield {"run_task_graph": p_run, "build_task_state": p_state}


# ---------------------------------------------------------------------------- #
#  OUTRAS FIXTURES DE OTIMIZAÇÃO (sem duplicação)
# ---------------------------------------------------------------------------- #
@pytest.fixture
def fast_notification_config() -> Generator[None, None, None]:
    with patch("time.sleep"), patch("requests.post") as p_post:
        p_post.return_value.status_code = 200
        yield


@pytest.fixture
def fast_retry_config() -> Dict[str, int]:
    return {"max_retries": 1, "retry_delay": 0, "timeout": 1}


@pytest.fixture
def mock_graph_execution() -> Generator[Dict[str, Any], None, None]:
    with patch("langgraph.graph.StateGraph.compile") as p_compile, \
         patch("langgraph.graph.CompiledGraph.invoke") as p_invoke:

        compiled = MagicMock()
        p_compile.return_value = compiled
        p_invoke.return_value = {"status": "COMPLETED", "result": "mock"}
        yield {"compile": p_compile, "invoke": p_invoke}


@pytest.fixture
def performance_tracker(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    start = time.perf_counter()
    yield
    dur = time.perf_counter() - start
    max_dur = float(os.getenv("MAX_TEST_DURATION", "5.0"))
    if dur > max_dur:
        pytest.fail(f"Test took {dur:.2f}s (> {max_dur}s)")


@pytest.fixture
def mock_crewai_agents() -> Generator[Dict[str, MagicMock], None, None]:
    with patch("crewai.Agent") as p_agent, patch("crewai.Crew") as p_crew:
        agent = MagicMock()
        agent.execute.return_value = {"status": "completed"}
        p_agent.return_value = agent

        crew = MagicMock()
        crew.kickoff.return_value = {"final_output": "ok"}
        p_crew.return_value = crew

        yield {"agent": agent, "crew": crew}


# ──────────────────────────────────────────────────────────────────────────────
#  MARCADORES CUSTOMIZADOS + AUTO-MARCAÇÃO
# ──────────────────────────────────────────────────────────────────────────────
def pytest_configure(config: pytest.Config) -> None:
    for key, desc in (
        ("unit", "fast unit tests"),
        ("integration", "integration tests"),
        ("slow", "tests >5s"),
        ("expensive", "requires RUN_EXPENSIVE_TESTS=true"),
        ("asyncio", "async tests"),
    ):
        config.addinivalue_line("markers", f"{key}: {desc}")


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]) -> None:
    """Aplica markers com base no cache de durações."""
    if not _DURATION_CACHE.exists():
        return
    try:
        content = _DURATION_CACHE.read_text().strip()
        if not content:
            return
        durations = json.loads(content)
    except json.JSONDecodeError:
        # If JSON is corrupted, skip duration-based marking
        return
    for item in items:
        dur = durations.get(item.nodeid)
        if dur is None:
            continue
        if dur <= _THRESHOLDS["unit"]:
            item.add_marker("unit")
        elif dur <= _THRESHOLDS["integration"]:
            item.add_marker("integration")
        else:
            item.add_marker("slow")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Atualiza cache de durações."""
    if report.when != "call":
        return
    data: Dict[str, float] = {}
    if _DURATION_CACHE.exists():
        try:
            content = _DURATION_CACHE.read_text().strip()
            if content:
                data = json.loads(content)
        except json.JSONDecodeError:
            # If JSON is corrupted, start with empty dict
            data = {}
    data[report.nodeid] = report.duration
    _DURATION_CACHE.write_text(json.dumps(data, indent=1))
