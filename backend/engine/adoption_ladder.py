"""Adoption ladder — each adopted feature unlocks the next adjacent suggestion.

Demonstrates compounding platform depth (Bill Pay → AutoPay → Credit Score →
Sweep FD), not a one-off nudge. Adopted features are read from the feedback
store, so the ladder advances as the user actually uses features.
"""
from __future__ import annotations

from typing import Any

LADDER = ["bill_pay", "autopay", "credit_score", "fixed_deposit"]

DISPLAY = {
    "bill_pay": "Bill Pay",
    "autopay": "AutoPay",
    "credit_score": "Credit Score",
    "fixed_deposit": "Sweep FD",
}


def next_after(feature: str) -> str | None:
    """The feature unlocked once `feature` is adopted."""
    if feature in LADDER:
        i = LADDER.index(feature)
        if i + 1 < len(LADDER):
            return LADDER[i + 1]
    return None


def state(adopted: set[str]) -> dict[str, Any]:
    """Ladder progress given the set of already-adopted features."""
    remaining = [f for f in LADDER if f not in adopted]
    nxt = remaining[0] if remaining else None
    return {
        "ladder": [{"feature": f, "display": DISPLAY[f], "adopted": f in adopted} for f in LADDER],
        "adopted": sorted(adopted),
        "next": nxt,
        "next_display": DISPLAY.get(nxt) if nxt else None,
    }
