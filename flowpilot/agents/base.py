from ..client import LLMClient
from ..config import Config


class BaseAgent:
    name: str = "base"
    system_prompt: str = ""

    def __init__(self, client: LLMClient | None = None, config: Config | None = None):
        self._owns_client = client is None
        self.client = client or LLMClient(config)
        self.config = config or Config()

    async def run(self, user_message: str, *, context: str = "") -> str:
        messages = [{"role": "system", "content": self.system_prompt}]
        if context:
            messages.append({"role": "user", "content": f"上下文：\n{context}"})
        messages.append({"role": "user", "content": user_message})
        return await self.client.chat(messages)

    async def close(self):
        if self._owns_client:
            await self.client.close()
