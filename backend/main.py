"""Saarthi backend — FastAPI app.

Milestone 1 surface: health + synthetic data access. Trigger engine, agent
loop, RAG, suitability, XAI and feedback routes are layered on in later
milestones.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import config
from engine import triggers

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


def _load_dataset() -> dict[str, Any]:
    if not config.TRANSACTIONS_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="Synthetic data not generated yet. Run: python data/generate.py",
        )
    with config.TRANSACTIONS_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def _dataset_now(data: dict[str, Any]) -> datetime:
    """Reference 'now' for detection — the dataset's anchor, so triggers are
    deterministic regardless of the real wall clock."""
    return datetime.fromisoformat(data["generated_at"])


def _require_persona(data: dict[str, Any], persona_id: str) -> list[dict[str, Any]]:
    txns = data["transactions"].get(persona_id)
    if txns is None:
        raise HTTPException(status_code=404, detail=f"Unknown persona '{persona_id}'")
    return txns


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
    moments = triggers.detect_all(persona_id, txns, _dataset_now(data))
    return {
        "persona_id": persona_id,
        "count": len(moments),
        "moments": [m.model_dump() for m in moments],
    }


@app.get("/triggers")
def all_triggers() -> dict[str, Any]:
    """Trigger sweep across every persona — handy for the demo dashboard."""
    data = _load_dataset()
    now = _dataset_now(data)
    out: dict[str, list[dict[str, Any]]] = {}
    for persona_id, txns in data["transactions"].items():
        out[persona_id] = [m.model_dump() for m in triggers.detect_all(persona_id, txns, now)]
    return {"generated_at": data["generated_at"], "triggers": out}
