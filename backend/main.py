"""Saarthi backend — FastAPI app.

Milestone 1 surface: health + synthetic data access. Trigger engine, agent
loop, RAG, suitability, XAI and feedback routes are layered on in later
milestones.
"""
from __future__ import annotations

import json
from datetime import datetime
from functools import lru_cache
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

import config
from data import generate as datagen
from engine import agent, comparison, feedback, rag, triggers
from models import TriggerType


class FeedbackIn(BaseModel):
    persona_id: str
    trigger_type: str
    outcome: str  # adopted | skipped | escalated
    detail: str | None = None  # e.g. the adopted feature (bill_pay) for the ladder

app = FastAPI(
    title="Saarthi — Agentic Adoption Copilot",
    description="Trust-first, agentic nudges inside a mocked YONO super-app.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def _load_dataset() -> dict[str, Any]:
    """Load the synthetic dataset. Prefer the generated file; if it's absent
    (e.g. a fresh serverless bundle), build it deterministically in memory."""
    if config.TRANSACTIONS_PATH.exists():
        with config.TRANSACTIONS_PATH.open(encoding="utf-8") as fh:
            return json.load(fh)
    return datagen.build()


def _dataset_now(data: dict[str, Any]) -> datetime:
    """Reference 'now' for detection — the dataset's anchor, so triggers are
    deterministic regardless of the real wall clock."""
    return datetime.fromisoformat(data["generated_at"])


def _require_persona(data: dict[str, Any], persona_id: str) -> list[dict[str, Any]]:
    txns = data["transactions"].get(persona_id)
    if txns is None:
        raise HTTPException(status_code=404, detail=f"Unknown persona '{persona_id}'")
    return txns


def _persona_meta(data: dict[str, Any], persona_id: str) -> dict[str, Any]:
    meta = next((p for p in data["personas"] if p["persona_id"] == persona_id), None)
    if meta is None:
        raise HTTPException(status_code=404, detail=f"Unknown persona '{persona_id}'")
    return meta


@app.get("/health")
def health() -> dict[str, Any]:
    """Liveness + environment sanity for the demo machine."""
    return {
        "status": "ok",
        "model": config.MODEL,
        "anthropic_key_present": config.has_api_key(),
        "data_generated": config.TRANSACTIONS_PATH.exists(),
    }


@app.get("/personas")
def list_personas() -> list[dict[str, Any]]:
    """The three seeded demo personas (without their full transaction history)."""
    data = _load_dataset()
    return data["personas"]


@app.get("/personas/{persona_id}/transactions")
def persona_transactions(persona_id: str) -> dict[str, Any]:
    """Full synthetic transaction stream for one persona."""
    data = _load_dataset()
    txns = _require_persona(data, persona_id)
    return {"persona_id": persona_id, "count": len(txns), "transactions": txns}


@app.get("/personas/{persona_id}/triggers")
def persona_triggers(persona_id: str) -> dict[str, Any]:
    """Run the trigger engine over one persona's stream -> candidate moments.

    This is the 'perceive + detect' stage. The agent core (M5) will decide
    whether any of these are actually worth surfacing.
    """
    data = _load_dataset()
    txns = _require_persona(data, persona_id)
    meta = _persona_meta(data, persona_id)
    moments = triggers.detect_all_moments(meta, txns, _dataset_now(data))
    return {
        "persona_id": persona_id,
        "count": len(moments),
        "moments": [m.model_dump(mode="json") for m in moments],
    }


@app.get("/triggers")
def all_triggers() -> dict[str, Any]:
    """Trigger sweep across every persona — handy for the demo dashboard."""
    data = _load_dataset()
    now = _dataset_now(data)
    out: dict[str, list[dict[str, Any]]] = {}
    for meta in data["personas"]:
        pid = meta["persona_id"]
        moments = triggers.detect_all_moments(meta, data["transactions"][pid], now)
        out[pid] = [m.model_dump(mode="json") for m in moments]
    return {"generated_at": data["generated_at"], "triggers": out}


@app.get("/rag")
def rag_search(q: str, k: int = 3) -> dict[str, Any]:
    """Grounded retrieval over the corpus — anti-hallucination layer / demo probe."""
    return {"query": q, "results": rag.query_rag(q, k)}


@app.get("/personas/{persona_id}/nudge")
def persona_nudge(persona_id: str) -> dict[str, Any]:
    """Run the agent loop over a persona's detected moments -> one decision.

    The agent decides whether to surface, picks + suitability-checks a product,
    grounds it, drafts the bilingual nudge, and returns its full decision log.
    """
    data = _load_dataset()
    txns = _require_persona(data, persona_id)
    meta = _persona_meta(data, persona_id)
    moments = [
        m.model_dump(mode="json")
        for m in triggers.detect_all_moments(meta, txns, _dataset_now(data))
    ]
    return agent.run_agent(
        meta,
        moments,
        skipped_types=feedback.skipped_categories(persona_id),
        adopted_features=feedback.adopted_features(persona_id),
    )


@app.post("/feedback")
def post_feedback(fb: FeedbackIn) -> dict[str, Any]:
    """Record an outcome (adopted/skipped/escalated) — closes the learn loop."""
    try:
        rec = feedback.record(fb.persona_id, fb.trigger_type, fb.outcome, fb.detail)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"recorded": rec, "summary": feedback.summary(fb.persona_id)}


@app.delete("/feedback/{persona_id}")
def reset_feedback(persona_id: str) -> dict[str, Any]:
    """Clear feedback for a persona — handy to re-run the demo cleanly."""
    feedback.reset(persona_id)
    return {"reset": persona_id}


@app.get("/personas/{persona_id}/comparison")
def persona_comparison(persona_id: str) -> dict[str, Any]:
    """Honest side-by-side comparison for a persona with a premium-leak moment.

    Derives the competitor from the detected trigger, then grounds every figure
    in the corpus (incl. at least one row where the competitor wins).
    """
    data = _load_dataset()
    txns = _require_persona(data, persona_id)
    moments = triggers.detect_all(persona_id, txns, _dataset_now(data))
    leak = next((m for m in moments if m.trigger_type is TriggerType.PREMIUM_LEAK), None)
    if leak is None:
        raise HTTPException(
            status_code=409,
            detail=f"No premium-leak moment for '{persona_id}' to compare against.",
        )
    result = comparison.build_insurance_comparison(leak.evidence.get("competitor"))
    if result is None:
        raise HTTPException(status_code=503, detail="Comparison corpus unavailable.")
    return {"persona_id": persona_id, "trigger": leak.model_dump(), "comparison": result}
