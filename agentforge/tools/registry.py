"""Tool registry and base tool interface."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ToolParameter:
    name: str
    type: str  # "string", "integer", "boolean", "array", "object"
    description: str
    required: bool = True


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)
    handler: Callable[..., Any] = field(default=None, repr=False)

    def to_openai_spec(self) -> dict:
        params = {}
        required = []
        for p in self.parameters:
            params[p.name] = {"type": p.type, "description": p.description}
            if p.required:
                required.append(p.name)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": params,
                    "required": required,
                },
            },
        }

    def to_prompt_spec(self) -> str:
        lines = [f"- {self.name}: {self.description}"]
        for p in self.parameters:
            req = "必填" if p.required else "可选"
            lines.append(f"    - {p.name} ({p.type}, {req}): {p.description}")
        return "\n".join(lines)


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition):
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def all_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def openai_tools_spec(self) -> list[dict]:
        return [t.to_openai_spec() for t in self._tools.values()]

    def tools_prompt(self) -> str:
        return "\n".join(t.to_prompt_spec() for t in self._tools.values())

    async def execute(self, name: str, arguments: dict[str, Any]) -> str:
        tool = self._tools.get(name)
        if not tool:
            return f"Error: unknown tool '{name}'"
        try:
            result = tool.handler(**arguments)
            if isinstance(result, str):
                return result
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Error executing '{name}': {e}"


# Global registry
registry = ToolRegistry()
