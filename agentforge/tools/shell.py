"""Shell execution tool."""

from __future__ import annotations

import subprocess

from .registry import ToolDefinition, ToolParameter, registry

SAFE_COMMANDS = {
    "git", "python", "pip", "node", "npm", "ls", "cat", "echo",
    "pytest", "ruff", "mypy", "black", "isort", "curl", "wget",
}


def run_command(command: str, timeout: int = 30) -> str:
    parts = command.split()
    if not parts or parts[0] not in SAFE_COMMANDS:
        return f"Blocked: command must start with one of {sorted(SAFE_COMMANDS)}"
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}"
        return output[:5000]
    except subprocess.TimeoutExpired:
        return f"Timeout after {timeout}s"
    except Exception as e:
        return f"Error: {e}"


registry.register(ToolDefinition(
    name="run_command",
    description="执行安全的 shell 命令（仅限白名单命令）",
    parameters=[
        ToolParameter("command", "string", "要执行的命令"),
        ToolParameter("timeout", "integer", "超时秒数", required=False),
    ],
    handler=run_command,
))
