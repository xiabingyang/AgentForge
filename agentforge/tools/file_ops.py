"""File operation tools."""

from __future__ import annotations

from pathlib import Path

from .registry import ToolDefinition, ToolParameter, registry


def read_file(path: str, encoding: str = "utf-8") -> str:
    return Path(path).read_text(encoding=encoding)


def write_file(path: str, content: str, encoding: str = "utf-8") -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding=encoding)
    return f"Written {len(content)} chars to {path}"


def list_directory(path: str = ".", pattern: str = "*") -> str:
    p = Path(path)
    entries = sorted(p.glob(pattern))
    lines = []
    for entry in entries:
        prefix = "DIR " if entry.is_dir() else "FILE"
        size = entry.stat().st_size if entry.is_file() else "-"
        lines.append(f"{prefix}  {entry.name}  ({size} bytes)")
    return "\n".join(lines) if lines else "(empty)"


def _register():
    registry.register(ToolDefinition(
        name="read_file",
        description="读取文件内容",
        parameters=[ToolParameter("path", "string", "文件路径")],
        handler=read_file,
    ))
    registry.register(ToolDefinition(
        name="write_file",
        description="写入文件内容",
        parameters=[
            ToolParameter("path", "string", "文件路径"),
            ToolParameter("content", "string", "文件内容"),
        ],
        handler=write_file,
    ))
    registry.register(ToolDefinition(
        name="list_directory",
        description="列出目录内容",
        parameters=[
            ToolParameter("path", "string", "目录路径", required=False),
            ToolParameter("pattern", "string", "glob 匹配模式", required=False),
        ],
        handler=list_directory,
    ))


_register()
