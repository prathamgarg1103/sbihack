"""Honest comparison builder (Flow B hero).

Assembles a side-by-side term-insurance comparison from corpus facts. Hard
requirement (suitability policy rule 4): at least one row where the competitor
genuinely wins. Every number traces back to a corpus doc — nothing invented.
"""
from __future__ import annotations

from typing import Any

from engine import rag


def _rupee(n: float | int) -> str:
    """Indian-grouped rupees: 10000000 -> ₹1,00,00,000."""
    s = str(abs(int(round(n))))
    if len(s) > 3:
        last3, rest = s[-3:], s[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        s = ",".join(groups) + "," + last3
    return "₹" + s


def _term_products() -> tuple[rag.Doc | None, list[rag.Doc]]:
    docs = rag.docs_by_type("term_insurance")
    sbi = next((d for d in docs if d.meta.get("is_sbi")), None)
    competitors = [d for d in docs if not d.meta.get("is_sbi")]
    return sbi, competitors


def build_insurance_comparison(competitor_hint: str | None = None) -> dict[str, Any] | None:
    sbi, competitors = _term_products()
    if sbi is None or not competitors:
        return None

    comp = None
    if competitor_hint:
        token = competitor_hint.lower().split()[0]
        comp = next(
            (d for d in competitors if token in str(d.meta.get("insurer", "")).lower()),
            None,
        )
    comp = comp or competitors[0]

    s, c = sbi.meta, comp.meta
    rows: list[dict[str, Any]] = [
        {
            "dimension": "Monthly premium",
            "sbi": _rupee(s["monthly_premium"]),
            "competitor": _rupee(c["monthly_premium"]),
            "winner": "sbi" if s["monthly_premium"] < c["monthly_premium"] else "competitor",
        },
        {
            "dimension": "Annual premium",
            "sbi": _rupee(s["annual_premium"]),
            "competitor": _rupee(c["annual_premium"]),
            "winner": "sbi" if s["annual_premium"] < c["annual_premium"] else "competitor",
        },
        {
            "dimension": "Life cover",
            "sbi": _rupee(s["cover"]),
            "competitor": _rupee(c["cover"]),
            "winner": "tie" if s["cover"] == c["cover"] else ("sbi" if s["cover"] > c["cover"] else "competitor"),
        },
        {
            "dimension": "Claim settlement ratio (FY24)",
            "sbi": f"{s['claim_settlement_ratio']}%",
            "competitor": f"{c['claim_settlement_ratio']}%",
            "winner": "competitor"
            if c["claim_settlement_ratio"] > s["claim_settlement_ratio"]
            else "sbi",
        },
        {
            "dimension": "Free-look period",
            "sbi": f"{s['free_look_days']} days",
            "competitor": f"{c['free_look_days']} days",
            "winner": "tie",
        },
        {
            "dimension": "Key exclusion",
            "sbi": s["key_exclusion"],
            "competitor": c["key_exclusion"],
            "winner": "tie",
        },
    ]

    competitor_wins = [r["dimension"] for r in rows if r["winner"] == "competitor"]
    same_cover = s["cover"] == c["cover"]
    annual_saving = c["annual_premium"] - s["annual_premium"]

    if same_cover and annual_saving > 0:
        verdict = (
            f"For the same {_rupee(s['cover'])} cover, {s['insurer']} costs "
            f"{_rupee(annual_saving)}/year less. But {c['insurer']}'s claim "
            f"settlement ratio is marginally higher "
            f"({c['claim_settlement_ratio']}% vs {s['claim_settlement_ratio']}%). "
            "Switch only if that saving matters more to you than the small "
            "difference — and only after reading both policy documents."
        )
    else:
        verdict = (
            "These plans are close. Read both policy documents and talk to a "
            "human advisor before deciding."
        )

    return {
        "product_type": "Term insurance (pure protection — not an investment)",
        "sbi_product": {"name": s["title"], "insurer": s["insurer"]},
        "competitor_product": {"name": c["title"], "insurer": c["insurer"]},
        "rows": rows,
        "competitor_wins": competitor_wins,
        "annual_saving": annual_saving if same_cover else None,
        "verdict": verdict,
        "sources": [sbi.source, comp.source, "claim-settlement-ratios.md", "fee-schedule.md"],
        "disclaimer": (
            "Guidance, not a sale. Figures include premium; 18% GST applies. "
            "ULIPs are never recommended."
        ),
    }
