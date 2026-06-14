"""RAG layer — grounding / anti-hallucination.

Pure-Python TF-IDF cosine retrieval over the local corpus. No heavy ML deps
(scikit-learn/numpy), which keeps the serverless bundle small — and for a
~10-doc corpus the result is identical in spirit to a vectorizer. Each corpus
doc carries YAML frontmatter (structured facts used by the comparison builder)
plus a body (indexed for retrieval), so the numbers the agent states and the
numbers a table shows share one source.

Upgrade path (README): swap this index for FAISS + sentence-transformers; the
`query_rag` / `get_doc` surface stays identical.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

import config

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
_TOKEN = re.compile(r"[a-z0-9]+")

# A small English stop-list (we don't pull in sklearn just for this).
_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is", "are",
    "be", "it", "this", "that", "with", "as", "at", "by", "from", "your", "you",
    "not", "no", "any", "if", "but", "so", "than", "into", "per", "only", "may",
}


def _tokens(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP]


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
    """Minimal TF-IDF cosine index."""

    def __init__(self, docs: list[Doc]):
        self.docs = docs
        toks = [_tokens(f"{d.title}\n{d.body}") for d in docs]
        n = len(docs)
        df: Counter[str] = Counter()
        for ts in toks:
            df.update(set(ts))
        # smoothed idf
        self._idf = {t: math.log((1 + n) / (1 + c)) + 1.0 for t, c in df.items()}
        self._vecs = [self._vectorize(ts) for ts in toks]
        self._norms = [math.sqrt(sum(w * w for w in v.values())) or 1.0 for v in self._vecs]

    def _vectorize(self, toks: list[str]) -> dict[str, float]:
        tf = Counter(toks)
        return {t: c * self._idf.get(t, 0.0) for t, c in tf.items()}

    def query(self, q: str, k: int = 3) -> list[tuple[Doc, float]]:
        qvec = self._vectorize(_tokens(q))
        qnorm = math.sqrt(sum(w * w for w in qvec.values())) or 1.0
        scored: list[tuple[Doc, float]] = []
        for doc, vec, norm in zip(self.docs, self._vecs, self._norms):
            small, large = (qvec, vec) if len(qvec) <= len(vec) else (vec, qvec)
            dot = sum(w * large.get(t, 0.0) for t, w in small.items())
            sim = dot / (qnorm * norm)
            if sim > 0:
                scored.append((doc, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]


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
