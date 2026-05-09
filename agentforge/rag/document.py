"""Document loader and parser."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Document:
    content: str
    metadata: dict

    @property
    def source(self) -> str:
        return self.metadata.get("source", "unknown")


class DocumentLoader:
    SUPPORTED_EXTENSIONS = {".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".csv"}

    @classmethod
    def load(cls, path: str) -> Document:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if p.suffix not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {p.suffix}")
        content = p.read_text(encoding="utf-8")
        return Document(
            content=content,
            metadata={"source": str(p), "filename": p.name, "extension": p.suffix, "size": len(content)},
        )

    @classmethod
    def load_text(cls, content: str, source: str = "upload") -> Document:
        return Document(content=content, metadata={"source": source, "size": len(content)})

    @classmethod
    def load_directory(cls, path: str, extensions: set[str] | None = None) -> list[Document]:
        exts = extensions or cls.SUPPORTED_EXTENSIONS
        p = Path(path)
        docs = []
        for file in sorted(p.rglob("*")):
            if file.is_file() and file.suffix in exts:
                docs.append(cls.load(str(file)))
        return docs
