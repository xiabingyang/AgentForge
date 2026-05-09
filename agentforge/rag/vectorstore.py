"""Simple in-memory vector store using numpy."""

from __future__ import annotations

import numpy as np


class VectorStore:
    def __init__(self):
        self._vectors: np.ndarray | None = None
        self._texts: list[str] = []
        self._metas: list[dict] = []

    def add(self, embeddings: list[list[float]], texts: list[str], metas: list[dict]):
        arr = np.array(embeddings, dtype=np.float32)
        # Normalize for cosine similarity via dot product
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1
        arr = arr / norms

        if self._vectors is None:
            self._vectors = arr
        else:
            self._vectors = np.vstack([self._vectors, arr])
        self._texts.extend(texts)
        self._metas.extend(metas)

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        if self._vectors is None or len(self._texts) == 0:
            return []
        q = np.array(query_embedding, dtype=np.float32)
        norm = np.linalg.norm(q)
        if norm > 0:
            q = q / norm
        scores = self._vectors @ q
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {"text": self._texts[i], "score": float(scores[i]), "metadata": self._metas[i]}
            for i in top_indices
            if scores[i] > 0
        ]

    @property
    def size(self) -> int:
        return len(self._texts)

    def clear(self):
        self._vectors = None
        self._texts = []
        self._metas = []
