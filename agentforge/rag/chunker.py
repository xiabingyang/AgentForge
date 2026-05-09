"""Text chunking strategies."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    index: int
    metadata: dict

    @property
    def source(self) -> str:
        return self.metadata.get("source", "unknown")


def chunk_by_chars(text: str, chunk_size: int = 500, overlap: int = 100, metadata: dict | None = None) -> list[Chunk]:
    meta = metadata or {}
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        piece = text[start:end]
        if piece.strip():
            chunks.append(Chunk(text=piece, index=idx, metadata={**meta, "char_start": start, "char_end": end}))
            idx += 1
        start += chunk_size - overlap
    return chunks


def chunk_by_paragraph(text: str, max_chunk_size: int = 800, metadata: dict | None = None) -> list[Chunk]:
    meta = metadata or {}
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    idx = 0
    for para in paragraphs:
        if len(current) + len(para) > max_chunk_size and current:
            chunks.append(Chunk(text=current, index=idx, metadata={**meta}))
            idx += 1
            current = para
        else:
            current = f"{current}\n\n{para}".strip() if current else para
    if current:
        chunks.append(Chunk(text=current, index=idx, metadata={**meta}))
    return chunks
