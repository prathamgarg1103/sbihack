"""Goal Engine (fold-in, not a standalone flow).

Turns a generic nudge into a goal-framed one ("move ₹450 to your bike goal —
you'd be 32% there"). It only adds framing + target math; the actual product
recommendation still routes through the suitability filter + RAG honest-math.
"""
from __future__ import annotations

from typing import Any


def primary_goal(persona: dict[str, Any]) -> dict[str, Any] | None:
    goals = persona.get("goals") or []
    return goals[0] if goals else None


def _sip_future_value(monthly: float, annual_pct: float, months: int) -> int:
    """Future value of a monthly contribution (ordinary annuity)."""
    i = annual_pct / 100 / 12
    if i == 0:
        return int(round(monthly * months))
    return int(round(monthly * (((1 + i) ** months - 1) / i)))


def invest_instead(
    monthly: float,
    rd_pct: float,
    sip_pct: float,
    horizons_years: tuple[int, ...] = (1, 3, 5),
) -> dict[str, Any]:
    """Illustrate redirecting `monthly` from an unused sub into an RD vs an SIP.

    Returns invested-vs-grown figures per horizon. Rates come from the corpus
    (illustrative; SIP is market-linked / not guaranteed — see the disclaimer)."""
    scenarios = []
    for years in horizons_years:
        months = years * 12
        invested = int(round(monthly * months))
        rd = _sip_future_value(monthly, rd_pct, months)
        sip = _sip_future_value(monthly, sip_pct, months)
        scenarios.append(
            {
                "years": years,
                "invested": invested,
                "rd_value": rd,
                "sip_value": sip,
                "sip_gain": sip - invested,
            }
        )
    return {
        "monthly": int(round(monthly)),
        "rd_pct": rd_pct,
        "sip_pct": sip_pct,
        "scenarios": scenarios,
        "disclaimer": (
            f"RD ~{rd_pct}% is fixed; the SIP {sip_pct}% figure is illustrative and "
            "market-linked — returns vary, can be negative, and are not guaranteed."
        ),
    }


def frame_redirect(goal: dict[str, Any], amount: float) -> dict[str, Any]:
    """Goal-framed redirect of `amount` toward `goal`, with before/after progress."""
    saved = float(goal.get("saved_so_far", 0))
    target = float(goal.get("target_amount", 0)) or 1.0
    new_saved = saved + amount
    pct_before = round(saved / target * 100)
    pct_after = round(new_saved / target * 100)
    label = goal.get("label", "your goal")
    amt = int(round(amount))
    return {
        "goal_id": goal.get("goal_id"),
        "label": label,
        "amount": amt,
        "saved_before": int(saved),
        "saved_after": int(new_saved),
        "target": int(target),
        "pct_before": pct_before,
        "pct_after": pct_after,
        "text": {
            "en": f"Move ₹{amt:,} to your {label} goal — you'd be {pct_after}% there.",
            "hi": f"₹{amt:,} अपने “{label}” लक्ष्य में डालें — आप {pct_after}% तक पहुँच जाएँगे।",
        },
    }
