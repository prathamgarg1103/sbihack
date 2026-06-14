"""RAG layer — grounding / anti-hallucination.

Lightweight TF-IDF cosine retrieval over the local corpus (no API key, instant
install). Each corpus doc carries YAML frontmatter (structured facts used by the
comparison builder) plus a body (indexed for free-text retrieval). Single source
of truth, so the numbers the agent states and the numbers a table shows cannot
drift apart.

Upgrade path (documented in README): swap TfidfVectorizer for FAISS +
sentence-transformers; the `query_rag` / `get_doc` surface stays identical.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import config

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


@dataclass
class Doc:
    id: str
    title: str
    doc_type: str
    body: str
    source: str
    meta: dict[str, Any] = field(default_factory=dict)


def _parse(path: Path) -> Doc:
    text = path.read_text(encoding="utf-8")
    m = _FRONTMATTER.match(text)
    if m:
        meta = yaml.safe_load(m.group(1)) or {}
        body = m.group(2).strip()
    else:
        meta, body = {}, text.strip()
    return Doc(
        id=str(meta.get("id", path.stem)),
        title=str(meta.get("title", path.stem)),
        doc_type=str(meta.get("doc_type", "")),
        body=body,
        source=path.name,
        meta=meta,
    )


class RagIndex:
    def __init__(self, docs: list[Doc]):
        self.docs = docs
        self._vec = TfidfVectorizer(stop_words="english")
        self._matrix = self._vec.fit_transform([f"{d.title}\n{d.body}" for d in docs])

    def query(self, q: str, k: int = 3) -> list[tuple[Doc, float]]:
        qv = self._vec.transform([q])
        sims = cosine_similarity(qv, self._matrix)[0]
        order = sims.argsort()[::-1][:k]
        return [(self.docs[i], float(sims[i])) for i in order if sims[i] > 0]


@lru_cache(maxsize=1)
def get_index() -> RagIndex:
    paths = sorted(config.CORPUS_DIR.glob("*.md"))
    if not paths:
        raise RuntimeError(f"No corpus docs found in {config.CORPUS_DIR}")
    return RagIndex([_parse(p) for p in paths])


def query_rag(q: str, k: int = 3) -> list[dict[str, Any]]:
    """Free-text retrieval -> grounded snippets with provenance."""
    return [
        {
            "id": d.id,
            "title": d.title,
            "source": d.source,
            "doc_type": d.doc_type,
            "score": round(score, 3),
            "snippet": d.body[:400],
        }
        for d, score in get_index().query(q, k)
    ]


def get_doc(doc_id: str) -> Doc | None:
    return next((d for d in get_index().docs if d.id == doc_id), None)


def docs_by_type(doc_type: str) -> list[Doc]:
    return [d for d in get_index().docs if d.doc_type == doc_type]
