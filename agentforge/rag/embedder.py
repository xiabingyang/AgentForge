"""Text embedding via OpenAI-compatible API."""

from __future__ import annotations

import httpx

from ..config import Config


class Embedder:
    def __init__(self, config: Config | None = None):
        self.config = config or Config()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={"Authorization": f"Bearer {self.config.api_key}"},
            timeout=60.0,
        ) as client:
            resp = await client.post("/embeddings", json={
                "model": self.config.model,
                "input": texts,
            })
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]

    async def embed_one(self, text: str) -> list[float]:
        results = await self.embed([text])
        return results[0]
