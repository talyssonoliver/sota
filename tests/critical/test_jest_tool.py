import json
import os
from pathlib import Path
import sys
from unittest.mock import MagicMock

sys.modules.setdefault("langchain_core.tools", MagicMock(BaseTool=object))
sys.modules.setdefault("langsmith", MagicMock())
sys.modules.setdefault("langsmith.client", MagicMock())
sys.modules.setdefault("chromadb", MagicMock())
sys.modules.setdefault("requests", MagicMock())
sys.modules.setdefault("httpx", MagicMock())

from tools.jest_tool import JestTool


def create_tool():
    project_root = Path(__file__).resolve().parents[2]
    return JestTool(str(project_root))


def test_extract_param():
    tool = create_tool()
    query = "generate test path: src/Button.tsx, code: export const Button = () => {}, type: component"
    assert tool._extract_param(query, "path") == "src/Button.tsx"
    assert tool._extract_param(query, "type") == "component"
    assert tool._extract_param(query, "code").startswith("export")


def test_generate_component_test():
    tool = create_tool()
    code = "import React from 'react'; export default function Button(){ return <button>Ok</button>; }"
    result = json.loads(tool._generate_test("src/Button.tsx", code, "component"))
    data = result["data"]
    assert data["test_type"] == "component"
    assert "Button" in data["test_code"]
    assert data["suggested_test_path"].endswith(".test.tsx")


def test_list_tests():
    tool = create_tool()
    result = json.loads(tool._list_tests("src/Button.tsx"))
    data = result["data"]
    assert data["component"] == "Button"
    assert isinstance(data["test_files"], list)


def test_run_test_missing_file(tmp_path):
    tool = create_tool()
    result = json.loads(tool._run_test("nonexistent.test.ts"))
    data = result["data"]
    assert not data["success"]


def test_get_coverage_filter():
    tool = create_tool()
    result = json.loads(tool._get_coverage("src/components/Button.tsx"))
    data = result["data"]
    assert data["coverage"]["files"][0]["path"] == "src/components/Button.tsx"
