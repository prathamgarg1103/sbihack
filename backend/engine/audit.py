"""Suitability certificate — a hash-chained compliance audit trail.

EVERY agent decision (surfaced OR suppressed) is appended to an append-only
SQLite log. Each record carries the previous record's SHA-256, so the chain is
tamper-evident: /audit/verify recomputes every hash and reports intact or the
first broken sequence number. Pitch framing: SBI can hand a regulator a
per-recommendation audit trail — trigger, suitability verdict, the devil's-
advocate objection, consent state and the action taken.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

import config

GENESIS = "0" * 64


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.FEEDBACK_DB)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            seq          INTEGER PRIMARY KEY AUTOINCREMENT,
            ts           TEXT NOT NULL,
            persona_id   TEXT NOT NULL,
            trigger_type TEXT NOT NULL,
            product      TEXT NOT NULL,
            action       TEXT NOT NULL,
            payload      TEXT NOT NULL,
            prev_hash    TEXT NOT NULL,
            hash         TEXT NOT NULL
        )
        """
    )
    return conn


def _core(ts: str, persona_id: str, trigger_type: str, product: str,
          action: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"ts": ts, "persona_id": persona_id, "trigger_type": trigger_type,
            "product": product, "action": action, "payload": payload}


def _hash(prev_hash: str, core: dict[str, Any]) -> str:
    blob = prev_hash + json.dumps(core, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def append(persona_id: str, trigger_type: str, product: str, action: str,
           payload: dict[str, Any]) -> dict[str, Any]:
    """Append one record, chained to the previous record's hash."""
    ts = datetime.now(timezone.utc).isoformat()
    with _conn() as conn:
        row = conn.execute("SELECT hash FROM audit_log ORDER BY seq DESC LIMIT 1").fetchone()
        prev = row[0] if row else GENESIS
        core = _core(ts, persona_id, trigger_type, product, action, payload)
        h = _hash(prev, core)
        cur = conn.execute(
            "INSERT INTO audit_log (ts, persona_id, trigger_type, product, action, "
            "payload, prev_hash, hash) VALUES (?,?,?,?,?,?,?,?)",
            (ts, persona_id, trigger_type, product, action,
             json.dumps(payload, ensure_ascii=False), prev, h),
        )
        seq = cur.lastrowid
    return {"seq": seq, **core, "prev_hash": prev, "hash": h}


def chain(limit: int = 0) -> list[dict[str, Any]]:
    """The full chain, oldest first. limit=0 means everything."""
    q = "SELECT seq, ts, persona_id, trigger_type, product, action, payload, prev_hash, hash " \
        "FROM audit_log ORDER BY seq ASC"
    with _conn() as conn:
        rows = conn.execute(q).fetchall()
    if limit:
        rows = rows[-limit:]
    keys = ("seq", "ts", "persona_id", "trigger_type", "product", "action",
            "payload", "prev_hash", "hash")
    out = []
    for r in rows:
        rec = dict(zip(keys, r))
        try:
            rec["payload"] = json.loads(rec["payload"])
        except (TypeError, ValueError):
            pass
        out.append(rec)
    return out


def verify() -> dict[str, Any]:
    """Walk the chain, recomputing every hash. Reports intact or first break."""
    records = chain()
    prev = GENESIS
    for r in records:
        core = _core(r["ts"], r["persona_id"], r["trigger_type"], r["product"],
                     r["action"], r["payload"])
        if r["prev_hash"] != prev or _hash(prev, core) != r["hash"]:
            return {"intact": False, "records": len(records), "broken_at": r["seq"]}
        prev = r["hash"]
    return {"intact": True, "records": len(records), "broken_at": None}


def record_decision(persona: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    """Extract the compliance-relevant fields from an agent decision and chain it."""
    surfaced = decision.get("surfaced_moment") or {}
    fit = decision.get("suitability") or {}
    da = decision.get("devils_advocate") or {}
    payload = {
        "suitability": {"suitable": fit.get("suitable"),
                        "blocks": fit.get("blocks"),
                        "reasons": fit.get("reasons")} if fit else None,
        "devils_advocate": {"objection": (da.get("objection") or {}).get("en"),
                            "strength": da.get("strength"),
                            "verdict": da.get("verdict")} if da else None,
        "consent_state": ("pending_user_opt_in" if decision.get("action") == "surface"
                          else "not_surfaced"),
        "suppress_reasons": decision.get("reason"),
        "attention_budget": decision.get("attention_budget"),
        "nudge_title": ((decision.get("nudge") or {}).get("title") or {}).get("en"),
        "engine": decision.get("engine"),
    }
    return append(
        persona_id=persona.get("persona_id", "?"),
        trigger_type=surfaced.get("trigger_type") or "none",
        product=str((decision.get("product") or {}).get("type")
                    or decision.get("flow") or "none"),
        action=decision.get("action", "?"),
        payload=payload,
    )


def reset() -> None:
    """Test/demo helper — the production story is append-only."""
    with _conn() as conn:
        conn.execute("DELETE FROM audit_log")
