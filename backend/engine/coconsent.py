"""Guardian / Sahayak co-consent (assisted mode).

For personas flagged `assisted_mode` (e.g. an elderly user), any product action
above `CO_CONSENT_THRESHOLD` requires a guardian's co-approval. The request
lives in SQLite as a tiny state machine: pending -> approved | declined.
Everything is mocked — the "guardian's phone" is a demo panel in the UI — but
the state machine and audit story are real.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

import config

# Actions at or above this rupee value need guardian co-approval.
CO_CONSENT_THRESHOLD = 10_000

_STATES = {"pending", "approved", "declined"}


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.FEEDBACK_DB)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS coconsent (
            id                TEXT PRIMARY KEY,
            persona_id        TEXT NOT NULL,
            action            TEXT NOT NULL,
            amount            REAL NOT NULL,
            guardian_name     TEXT,
            guardian_relation TEXT,
            status            TEXT NOT NULL,
            created_ts        TEXT NOT NULL,
            decided_ts        TEXT
        )
        """
    )
    return conn


def gate(persona: dict[str, Any], amount: float, action: str = "adopt") -> dict[str, Any] | None:
    """If this persona+amount needs co-consent, return the gate payload for the
    UI (guardian, threshold, bilingual note); otherwise None."""
    if not persona.get("assisted_mode") or not amount or amount < CO_CONSENT_THRESHOLD:
        return None
    g = persona.get("guardian") or {}
    name = g.get("name", "your guardian")
    rel = g.get("relation", "guardian")
    rel_hi = g.get("relation_hi", rel)
    return {
        "required": True,
        "threshold": CO_CONSENT_THRESHOLD,
        "amount": int(round(amount)),
        "action": action,
        "guardian": g,
        "note": {
            "en": (f"This involves ₹{amount:,.0f} — above the ₹{CO_CONSENT_THRESHOLD:,} "
                   f"assisted-mode limit. {name} ({rel}) must co-approve first."),
            "hi": (f"इसमें ₹{amount:,.0f} शामिल हैं — सहायता-मोड की ₹{CO_CONSENT_THRESHOLD:,} "
                   f"सीमा से ऊपर। पहले {name} ({rel_hi}) की सह-मंज़ूरी ज़रूरी है।"),
        },
    }


def request(persona_id: str, action: str, amount: float,
            guardian: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create a pending co-consent request; returns the full record."""
    g = guardian or {}
    rec = {
        "id": uuid.uuid4().hex[:12],
        "persona_id": persona_id,
        "action": action,
        "amount": float(amount),
        "guardian_name": g.get("name"),
        "guardian_relation": g.get("relation"),
        "status": "pending",
        "created_ts": datetime.now(timezone.utc).isoformat(),
        "decided_ts": None,
    }
    with _conn() as conn:
        conn.execute(
            "INSERT INTO coconsent (id, persona_id, action, amount, guardian_name, "
            "guardian_relation, status, created_ts, decided_ts) VALUES (?,?,?,?,?,?,?,?,?)",
            (rec["id"], rec["persona_id"], rec["action"], rec["amount"], rec["guardian_name"],
             rec["guardian_relation"], rec["status"], rec["created_ts"], rec["decided_ts"]),
        )
    return rec


def get(request_id: str) -> dict[str, Any] | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT id, persona_id, action, amount, guardian_name, guardian_relation, "
            "status, created_ts, decided_ts FROM coconsent WHERE id = ?",
            (request_id,),
        ).fetchone()
    if row is None:
        return None
    keys = ("id", "persona_id", "action", "amount", "guardian_name", "guardian_relation",
            "status", "created_ts", "decided_ts")
    return dict(zip(keys, row))


def decide(request_id: str, approve: bool) -> dict[str, Any]:
    """State machine: only a PENDING request may move to approved/declined."""
    rec = get(request_id)
    if rec is None:
        raise ValueError(f"unknown co-consent request '{request_id}'")
    if rec["status"] != "pending":
        raise ValueError(f"request '{request_id}' already {rec['status']} — cannot re-decide")
    status = "approved" if approve else "declined"
    ts = datetime.now(timezone.utc).isoformat()
    with _conn() as conn:
        conn.execute(
            "UPDATE coconsent SET status = ?, decided_ts = ? WHERE id = ?",
            (status, ts, request_id),
        )
    rec.update({"status": status, "decided_ts": ts})
    return rec


def reset(persona_id: str | None = None) -> None:
    with _conn() as conn:
        if persona_id:
            conn.execute("DELETE FROM coconsent WHERE persona_id = ?", (persona_id,))
        else:
            conn.execute("DELETE FROM coconsent")
