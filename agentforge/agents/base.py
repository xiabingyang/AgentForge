from __future__ import annotations

import json
import re

from ..client import LLMClient
from ..config import Config
from ..tools.registry import ToolRegistry, registry as global_registry


class BaseAgent:
    name: str = "base"
    system_prompt: str = ""

    def __init__(
        self,
        client: LLMClient | None = None,
        config: Config | None = None,
        tools: ToolRegistry | None = None,
    ):
        self._owns_client = client is None
        self.client = client or LLMClient(config)
        self.config = config or Config()
        self.tools = tools or global_registry
        self._history: list[dict] = []

    async def run(self, user_message: str, *, context: str = "", max_tool_rounds: int = 5) -> str:
        messages = [{"role": "system", "content": self._build_system_prompt()}]
        if context:
            messages.append({"role": "user", "content": f"参考知识库内容：\n{context}"})
        messages.append({"role": "user", "content": user_message})

        self._history = list(messages)

        for _ in range(max_tool_rounds + 1):
            response = await self.client.chat(messages)
            messages.append({"role": "assistant", "content": response})

            tool_calls = self._parse_tool_calls(response)
            if not tool_calls:
                return response

            for call in tool_calls:
                result = await self.tools.execute(call["name"], call["arguments"])
                tool_msg = f"[Tool Result: {call['name']}]\n{result}"
                messages.append({"role": "user", "content": tool_msg})

        return response

    def _build_system_prompt(self) -> str:
        prompt = self.system_prompt
        if self.tools.all_tools():
            prompt += "\n\n你可以使用以下工具，通过 JSON 格式调用：\n"
            prompt += self.tools.tools_prompt()
            prompt += '\n\n调用格式：```tool\n{"name": "工具名", "arguments": {"参数": "值"}}\n```'
        return prompt

    def _parse_tool_calls(self, text: str) -> list[dict]:
        pattern = r"```tool\s*\n(.*?)\n```"
        matches = re.findall(pattern, text, re.DOTALL)
        calls = []
        for match in matches:
            try:
                parsed = json.loads(match.strip())
                if "name" in parsed:
                    calls.append({"name": parsed["name"], "arguments": parsed.get("arguments", {})})
            except json.JSONDecodeError:
                continue
        return calls

    async def close(self):
        if self._owns_client:
            await self.client.close()
