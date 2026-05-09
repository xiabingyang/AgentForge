import pytest

from flowpilot.config import Config
from flowpilot.tools.registry import ToolDefinition, ToolParameter, ToolRegistry
from flowpilot.tools.file_ops import read_file, write_file, list_directory
from flowpilot.tools.code_analysis import analyze_python, count_lines
from flowpilot.tools.shell import run_command


def test_tool_definition_spec():
    tool = ToolDefinition(
        name="test_tool",
        description="A test tool",
        parameters=[ToolParameter("path", "string", "File path")],
        handler=lambda path: f"read: {path}",
    )
    spec = tool.to_openai_spec()
    assert spec["type"] == "function"
    assert spec["function"]["name"] == "test_tool"
    assert "path" in spec["function"]["parameters"]["properties"]


def test_tool_registry_register():
    reg = ToolRegistry()
    tool = ToolDefinition(name="demo", description="demo tool", handler=lambda: "ok")
    reg.register(tool)
    assert reg.get("demo") is not None
    assert len(reg.all_tools()) == 1


def test_tool_registry_execute():
    reg = ToolRegistry()
    reg.register(ToolDefinition(
        name="echo",
        description="Echo input",
        parameters=[ToolParameter("text", "string", "Text to echo")],
        handler=lambda text: f"echo: {text}",
    ))
    import asyncio
    result = asyncio.run(reg.execute("echo", {"text": "hello"}))
    assert result == "echo: hello"


def test_tool_registry_unknown():
    reg = ToolRegistry()
    import asyncio
    result = asyncio.run(reg.execute("nonexistent", {}))
    assert "unknown" in result.lower()


def test_file_ops(tmp_path):
    test_file = tmp_path / "test.txt"
    write_file(str(test_file), "hello world")
    content = read_file(str(test_file))
    assert content == "hello world"


def test_list_directory(tmp_path):
    (tmp_path / "a.py").write_text("print('a')")
    (tmp_path / "b.txt").write_text("hello")
    result = list_directory(str(tmp_path))
    assert "a.py" in result
    assert "b.txt" in result


def test_code_analysis(tmp_path):
    py = tmp_path / "sample.py"
    py.write_text("def foo(x):\n    return x + 1\n")
    result = analyze_python(str(py))
    import json
    data = json.loads(result)
    assert any(f["name"] == "foo" for f in data["functions"])


def test_count_lines(tmp_path):
    py = tmp_path / "lines.py"
    py.write_text("line1\n\n# comment\nline4\n")
    result = count_lines(str(py))
    import json
    data = json.loads(result)
    assert data["total"] == 4


def test_shell_blocked():
    result = run_command("rm -rf /")
    assert "Blocked" in result
