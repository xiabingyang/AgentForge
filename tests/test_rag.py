import pytest

from agentforge.rag.document import DocumentLoader
from agentforge.rag.chunker import chunk_by_chars, chunk_by_paragraph
from agentforge.rag.vectorstore import VectorStore
import numpy as np


def test_document_loader(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello world", encoding="utf-8")
    doc = DocumentLoader.load(str(f))
    assert doc.content == "hello world"
    assert doc.metadata["filename"] == "test.txt"


def test_document_loader_text():
    doc = DocumentLoader.load_text("some content", source="manual")
    assert doc.content == "some content"
    assert doc.source == "manual"


def test_chunk_by_chars():
    text = "a" * 1200
    chunks = chunk_by_chars(text, chunk_size=500, overlap=100)
    assert len(chunks) >= 2
    assert chunks[0].text == "a" * 500


def test_chunk_by_paragraph():
    text = "Para one.\n\nPara two.\n\nPara three."
    chunks = chunk_by_paragraph(text, max_chunk_size=800)
    assert len(chunks) >= 1


def test_vectorstore():
    store = VectorStore()
    embeddings = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    texts = ["doc about cats", "doc about dogs", "doc about fish"]
    metas = [{"id": 0}, {"id": 1}, {"id": 2}]
    store.add(embeddings, texts, metas)
    assert store.size == 3

    results = store.search([1.0, 0.1, 0.0], top_k=2)
    assert len(results) == 2
    assert results[0]["text"] == "doc about cats"
    assert results[0]["score"] > 0


def test_vectorstore_clear():
    store = VectorStore()
    store.add([[1.0, 0.0]], ["text"], [{}])
    assert store.size == 1
    store.clear()
    assert store.size == 0


def test_vectorstore_empty_search():
    store = VectorStore()
    results = store.search([1.0, 0.0], top_k=5)
    assert results == []
