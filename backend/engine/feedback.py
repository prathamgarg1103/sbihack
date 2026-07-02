"""Feedback store — the 'learn' close of the loop, plus the attention budget.

Records adopted / skipped / escalated outcomes in SQLite. The agent reads recent
skips so a dismissed category is suppressed next time rather than repeated
(suitability rule 6). This is what turns a one-shot recommender into a loop that
adapts to the user.

Also persists the ATTENTION BUDGET: Diya may interrupt each user at most
`ATTENTION_CAP` times per calendar month. Every surfaced nudge spends 1; the
agent checks the remaining budget BEFORE surfacing and suppresses when it is
exhausted (or not worth the last interruption).
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

import config

VALID_OUTCOMES = {"adopted", "skipped", "escalated"}

# Hard cap on nudge interruptions per user per calendar month.
ATTENTION_CAP = 4


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.FEEDBACK_DB)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            persona_id  TEXT NOT NULL,
            trigger_type TEXT NOT NULL,
            outcome     TEXT NOT NULL,
            detail      TEXT,
            ts          TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS attention_spend (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            persona_id  TEXT NOT NULL,
            month       TEXT NOT NULL,
            ts          TEXT NOT NULL
        )
        """
    )
    # Migrate older DBs that predate the `detail` column.
    cols = {r[1] for r in conn.execute("PRAGMA table_info(feedback)").fetchall()}
    if "detail" not in cols:
        conn.execute("ALTER TABLE feedback ADD COLUMN detail TEXT")
    return conn


def _month_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def budget_status(persona_id: str) -> dict[str, Any]:
    """How much of this month's interruption budget remains for a persona."""
    month = _month_key()
    with _conn() as conn:
        used = conn.execute(
            "SELECT COUNT(*) FROM attention_spend WHERE persona_id = ? AND month = ?",
            (persona_id, month),
        ).fetchone()[0]
    return {
        "used": used,
        "cap": ATTENTION_CAP,
        "remaining": max(0, ATTENTION_CAP - used),
        "month": month,
    }


def spend_budget(persona_id: str) -> dict[str, Any]:
    """Spend 1 interruption (call ONLY when a nudge is actually surfaced)."""
    with _conn() as conn:
        conn.execute(
            "INSERT INTO attention_spend (persona_id, month, ts) VALUES (?, ?, ?)",
            (persona_id, _month_key(), datetime.now(timezone.utc).isoformat()),
        )
    return budget_status(persona_id)


def record(persona_id: str, trigger_type: str, outcome: str, detail: str | None = None) -> dict[str, Any]:
    if outcome not in VALID_OUTCOMES:
        raise ValueError(f"outcome must be one of {sorted(VALID_OUTCOMES)}")
    ts = datetime.now(timezone.utc).isoformat()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO feedback (persona_id, trigger_type, outcome, detail, ts) VALUES (?, ?, ?, ?, ?)",
            (persona_id, trigger_type, outcome, detail, ts),
        )
    return {"persona_id": persona_id, "trigger_type": trigger_type, "outcome": outcome,
            "detail": detail, "ts": ts}


def adopted_features(persona_id: str) -> set[str]:
    """Features the persona has adopted (detail of adopted feature_discovery rows)."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT detail FROM feedback "
            "WHERE persona_id = ? AND outcome = 'adopted' AND detail IS NOT NULL",
            (persona_id,),
        ).fetchall()
    return {r[0] for r in rows}


def skipped_categories(persona_id: str) -> set[str]:
    """Trigger types this persona has skipped — suppress these next time."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT trigger_type FROM feedback WHERE persona_id = ? AND outcome = 'skipped'",
            (persona_id,),
        ).fetchall()
    return {r[0] for r in rows}


def summary(persona_id: str) -> dict[str, int]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT outcome, COUNT(*) FROM feedback WHERE persona_id = ? GROUP BY outcome",
            (persona_id,),
        ).fetchall()
    return {outcome: count for outcome, count in rows}


def reset(persona_id: str | None = None) -> None:
    """Clear feedback AND attention-budget spend (handy to re-run the demo)."""
    with _conn() as conn:
        if persona_id:
            conn.execute("DELETE FROM feedback WHERE persona_id = ?", (persona_id,))
            conn.execute("DELETE FROM attention_spend WHERE persona_id = ?", (persona_id,))
        else:
            conn.execute("DELETE FROM feedback")
            conn.execute("DELETE FROM attention_spend")
