import os
from pathlib import Path
import sys
from unittest.mock import MagicMock
import pytest

sys.modules.setdefault("supabase", MagicMock())
sys.modules.setdefault("langchain_core.tools", MagicMock(BaseTool=object))
sys.modules.setdefault("langsmith", MagicMock())
sys.modules.setdefault("langsmith.client", MagicMock())
sys.modules.setdefault("chromadb", MagicMock())
sys.modules.setdefault("requests", MagicMock())
sys.modules.setdefault("httpx", MagicMock())

from tools.supabase_tool import SupabaseTool


def create_tool(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    project_root = Path(__file__).resolve().parents[2]
    monkeypatch.chdir(project_root)
    return SupabaseTool()


def test_plan_recognizes_actions(monkeypatch):
    tool = create_tool(monkeypatch)
    assert tool.plan("show schema")["action"] == "get_schema"
    assert tool.plan("service pattern example")["action"] == "get_service_pattern"
    assert tool.plan("SELECT * FROM products")["action"] == "execute_query"
    assert tool.plan("hello")["action"] == "generic_response"


def test_get_mock_schema(monkeypatch):
    tool = create_tool(monkeypatch)
    schema = tool._get_mock_schema()
    assert "Database" in schema


def test_run_returns_mock_data(monkeypatch):
    tool = create_tool(monkeypatch)
    result = tool._run("SELECT * FROM products")
    assert "Handmade Ceramic Mug" in result


def test_get_service_pattern(monkeypatch):
    tool = create_tool(monkeypatch)
    pattern = tool._get_service_pattern()
    assert "Service" in pattern
