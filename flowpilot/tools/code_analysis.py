"""Code analysis tools."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from .registry import ToolDefinition, ToolParameter, registry


def analyze_python(path: str) -> str:
    source = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    result = {"file": path, "classes": [], "functions": [], "imports": []}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            result["classes"].append({"name": node.name, "line": node.lineno, "methods": methods})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not isinstance(getattr(node, '_parent', None), ast.ClassDef):
            result["functions"].append({"name": node.name, "line": node.lineno, "args": [a.arg for a in node.args.args]})
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names] if hasattr(node, 'names') else []
            if isinstance(node, ast.ImportFrom) and node.module:
                result["imports"].append(node.module)
    return json.dumps(result, ensure_ascii=False, indent=2)


def count_lines(path: str, include_blank: bool = False) -> str:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    total = len(lines)
    code = sum(1 for l in lines if l.strip() and not l.strip().startswith("#")) if not include_blank else total
    blank = total - code
    comment = sum(1 for l in lines if l.strip().startswith("#"))
    return json.dumps({"file": path, "total": total, "code": code, "blank": blank, "comment": comment})


def _register():
    registry.register(ToolDefinition(
        name="analyze_python",
        description="分析 Python 文件结构（类、函数、导入）",
        parameters=[ToolParameter("path", "string", "Python 文件路径")],
        handler=analyze_python,
    ))
    registry.register(ToolDefinition(
        name="count_lines",
        description="统计代码行数",
        parameters=[ToolParameter("path", "string", "文件路径")],
        handler=count_lines,
    ))


_register()
