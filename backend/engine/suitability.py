"""Suitability filter — hard rules that override any recommendation.

These are the non-negotiable guardrails from the suitability policy (corpus doc
`suitability-policy.md`). The agent core calls `check_suitability` before it is
allowed to surface anything; a block here suppresses the nudge no matter what
the model "wants" to do.
"""
from __future__ import annotations

from typing import Any

# Insurance-cum-investment products are never recommended (rule 1).
BLOCKED_PRODUCT_TYPES = {
    "ulip",
    "insurance_cum_investment",
    "endowment",
    "money_back",
}

# A recurring premium shouldn't eat more than this share of monthly income.
MAX_PREMIUM_INCOME_PCT = 0.10


def check_suitability(
    *,
    product_type: str,
    monthly_cost: float = 0.0,
    persona: dict[str, Any] | None = None,
    recently_skipped: bool = False,
) -> dict[str, Any]:
    """Return a structured verdict. `suitable` is False if ANY block fires."""
    persona = persona or {}
    blocks: list[str] = []
    reasons: list[str] = []

    norm = product_type.strip().lower().replace("-", "_").replace(" ", "_")

    # Rule 1 — block insurance-cum-investment.
    if norm in BLOCKED_PRODUCT_TYPES:
        blocks.append(
            f"'{product_type}' is an insurance-cum-investment product — auto-blocked "
            "(Diya recommends simple term/deposit products only)."
        )

    # Rule — affordability.
    income = float(persona.get("monthly_income", 0) or 0)
    if income and monthly_cost > income * MAX_PREMIUM_INCOME_PCT:
        cap = round(income * MAX_PREMIUM_INCOME_PCT)
        blocks.append(
            f"Monthly cost ₹{round(monthly_cost):,} exceeds {int(MAX_PREMIUM_INCOME_PCT * 100)}% "
            f"of monthly income (₹{cap:,} cap) — over budget."
        )

    # Rule 6 — suppress recently-skipped categories.
    if recently_skipped:
        blocks.append("User recently skipped this category — suppress rather than repeat.")

    suitable = not blocks
    if suitable:
        reasons.append(
            f"'{product_type}' is a simple, suitable product"
            + (f" within budget (≤{int(MAX_PREMIUM_INCOME_PCT * 100)}% of income)." if income else ".")
        )

    return {
        "product_type": product_type,
        "suitable": suitable,
        "blocks": blocks,
        "reasons": reasons,
    }
