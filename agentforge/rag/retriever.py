"""RAG retriever — ties together document loading, chunking, embedding, and search."""

from __future__ import annotations

from dataclasses import dataclass, field

from .chunker import Chunk, chunk_by_chars, chunk_by_paragraph
from .document import Document, DocumentLoader
from .embedder import Embedder
from .vectorstore import VectorStore


@dataclass
class RetrievalResult:
    text: str
    score: float
    metadata: dict


class Retriever:
    def __init__(self, embedder: Embedder | None = None):
        self.embedder = embedder or Embedder()
        self.store = VectorStore()
        self._documents: list[Document] = []
        self._chunks: list[Chunk] = []

    async def add_document(self, doc: Document, chunk_size: int = 500, overlap: int = 100):
        self._documents.append(doc)
        chunks = chunk_by_chars(doc.content, chunk_size=chunk_size, overlap=overlap, metadata=doc.metadata)
        self._chunks.extend(chunks)
        if chunks:
            texts = [c.text for c in chunks]
            embeddings = await self.embedder.embed(texts)
            self.store.add(embeddings, texts, [c.metadata for c in chunks])

    async def add_text(self, content: str, source: str = "upload"):
        doc = DocumentLoader.load_text(content, source)
        await self.add_document(doc)

    async def query(self, question: str, top_k: int = 5) -> list[RetrievalResult]:
        query_emb = await self.embedder.embed_one(question)
        hits = self.store.search(query_emb, top_k=top_k)
        return [RetrievalResult(text=h["text"], score=h["score"], metadata=h["metadata"]) for h in hits]

    def build_context(self, results: list[RetrievalResult], max_chars: int = 3000) -> str:
        parts = []
        total = 0
        for r in results:
            if total + len(r.text) > max_chars:
                break
            parts.append(f"[{r.metadata.get('source', 'doc')}]\n{r.text}")
            total += len(r.text)
        return "\n\n---\n\n".join(parts)

    @property
    def document_count(self) -> int:
        return len(self._documents)

    @property
    def chunk_count(self) -> int:
        return self.store.size

    def clear(self):
        self.store.clear()
        self._documents = []
        self._chunks = []
