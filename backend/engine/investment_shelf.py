"""Open-shelf investments builder (New Earner / Flow C payoff).

The investment-breadth thesis, made concrete: YONO should list the WHOLE market —
SBI's own funds AND competitors', plus the full equity universe — not just SBI's
products. Diya layers honest guidance on top (including pointing to a non-SBI
fund when it genuinely wins). Every figure is grounded in the corpus and clearly
labelled illustrative — no live quotes, no fabricated numbers.
"""
from __future__ import annotations

from typing import Any

from engine import rag


def build_shelf() -> dict[str, Any] | None:
    doc = rag.get_doc("yono-investment-shelf")
    if doc is None:
        return None
    m = doc.meta
    funds = list(m.get("funds", []))
    stocks = list(m.get("stocks", []))
    sbi_funds = sum(1 for f in funds if f.get("is_sbi"))
    return {
        "funds": funds,
        "stocks": stocks,
        "fund_count": len(funds),
        "stock_count": len(stocks),
        "sbi_fund_count": sbi_funds,
        "other_fund_count": len(funds) - sbi_funds,
        "neutrality_note": m.get("neutrality_note", ""),
        "honest_highlight": m.get("honest_highlight", ""),
        "illustrative": bool(m.get("illustrative", True)),
        "disclaimer": (
            "Illustrative catalogue for the demo — not live quotes. Returns are "
            "market-linked, can be negative, and are not guaranteed. SIPs and index "
            "funds are simple, non-ULIP products that pass the suitability filter."
        ),
        "sources": [doc.source, "invest-instead-returns.md", "suitability-policy.md"],
    }
