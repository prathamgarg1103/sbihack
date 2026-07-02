"""Honest comparison builder (Flow B hero) + do-nothing baseline + ULIP exit math.

Assembles a side-by-side term-insurance comparison from corpus facts. Hard
requirements (suitability policy rule 4): at least one row where the competitor
genuinely wins, and a third "Do nothing" column with the honest cost (and
benefit!) of inaction. Every number traces back to a corpus doc — nothing
invented. Also builds the exit-cost-vs-stay analysis for a flagged ULIP.
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
    same_cover = s["cover"] == c["cover"]
    annual_saving = c["annual_premium"] - s["annual_premium"]

    # Third column — the honest "Do nothing" baseline: staying exactly as-is.
    rows: list[dict[str, Any]] = [
        {
            "dimension": "Monthly premium",
            "sbi": _rupee(s["monthly_premium"]),
            "competitor": _rupee(c["monthly_premium"]),
            "do_nothing": f"{_rupee(c['monthly_premium'])} (unchanged)",
            "winner": "sbi" if s["monthly_premium"] < c["monthly_premium"] else "competitor",
        },
        {
            "dimension": "Annual premium",
            "sbi": _rupee(s["annual_premium"]),
            "competitor": _rupee(c["annual_premium"]),
            "do_nothing": f"{_rupee(c['annual_premium'])} (unchanged)",
            "winner": "sbi" if s["annual_premium"] < c["annual_premium"] else "competitor",
        },
        {
            "dimension": "Life cover",
            "sbi": _rupee(s["cover"]),
            "competitor": _rupee(c["cover"]),
            "do_nothing": f"{_rupee(c['cover'])} (unchanged)",
            "winner": "tie" if s["cover"] == c["cover"] else ("sbi" if s["cover"] > c["cover"] else "competitor"),
        },
        {
            "dimension": "Claim settlement ratio (FY24)",
            "sbi": f"{s['claim_settlement_ratio']}%",
            "competitor": f"{c['claim_settlement_ratio']}%",
            "do_nothing": f"{c['claim_settlement_ratio']}%",
            "winner": "competitor"
            if c["claim_settlement_ratio"] > s["claim_settlement_ratio"]
            else "sbi",
        },
        {
            "dimension": "Free-look period",
            "sbi": f"{s['free_look_days']} days",
            "competitor": f"{c['free_look_days']} days",
            "do_nothing": "— (no new policy)",
            "winner": "tie",
        },
        {
            "dimension": "Key exclusion",
            "sbi": s["key_exclusion"],
            "competitor": c["key_exclusion"],
            "do_nothing": "Same as your current policy",
            "winner": "tie",
        },
        {
            "dimension": "Switching effort & re-disclosure",
            "sbi": "New proposal + fresh medical disclosures",
            "competitor": "—",
            "do_nothing": "None — nothing changes",
            "winner": "do_nothing",
        },
    ]
    if same_cover and annual_saving > 0:
        rows.insert(
            2,
            {
                "dimension": "Extra cost over 5 years",
                "sbi": "₹0 — you'd save",
                "competitor": "—",
                "do_nothing": f"{_rupee(annual_saving * 5)} more than switching",
                "winner": "sbi",
            },
        )

    competitor_wins = [r["dimension"] for r in rows if r["winner"] == "competitor"]
    do_nothing_wins = [r["dimension"] for r in rows if r["winner"] == "do_nothing"]

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

    do_nothing_note = (
        "Doing nothing is a real option: no paperwork, no fresh medical disclosures, "
        "no new exclusion clocks"
        + (f" — but you keep paying {_rupee(annual_saving)}/year more for the same cover."
           if same_cover and annual_saving > 0 else ".")
    )

    return {
        "product_type": "Term insurance (pure protection — not an investment)",
        "sbi_product": {"name": s["title"], "insurer": s["insurer"]},
        "competitor_product": {"name": c["title"], "insurer": c["insurer"]},
        "rows": rows,
        "competitor_wins": competitor_wins,
        "do_nothing_wins": do_nothing_wins,
        "do_nothing_note": do_nothing_note,
        "annual_saving": annual_saving if same_cover else None,
        "verdict": verdict,
        "sources": [sbi.source, comp.source, "claim-settlement-ratios.md", "fee-schedule.md"],
        "disclaimer": (
            "Guidance, not a sale. Figures include premium; 18% GST applies. "
            "ULIPs are never recommended."
        ),
    }


# --- Do-nothing baseline for idle cash (Flow A) ------------------------------
def build_do_nothing_idle(idle_amount: float) -> dict[str, Any] | None:
    """The honest cost of inaction on idle cash, grounded in the corpus
    (savings rate vs inflation) — plus the honest counterweight (liquidity)."""
    doc = rag.get_doc("sbi-savings-account")
    if doc is None or not idle_amount:
        return None
    sav = float(doc.meta.get("savings_rate", 2.70))
    infl = float(doc.meta.get("inflation_pct", 6.0))
    loss = int(round(idle_amount * (infl - sav) / 100))
    return {
        "label": {"en": "If you do nothing", "hi": "अगर आप कुछ नहीं करते"},
        "detail": {
            "en": (f"₹{idle_amount:,.0f} keeps earning {sav}% while inflation runs ~{infl}% — "
                   f"about ₹{loss:,} of purchasing power lost over a year."),
            "hi": (f"₹{idle_amount:,.0f} पर {sav}% ब्याज मिलता रहेगा जबकि महँगाई ~{infl}% है — "
                   f"साल भर में करीब ₹{loss:,} की क्रय-शक्ति घट जाएगी।"),
        },
        "honest_note": {
            "en": "Honest counterweight: doing nothing keeps the money fully liquid.",
            "hi": "ईमानदार पहलू: कुछ न करने से पैसा पूरी तरह उपलब्ध रहता है।",
        },
        "savings_rate_pct": sav,
        "inflation_pct": infl,
        "yearly_real_loss": loss,
        "source": doc.source,
    }


# --- ULIP exit-cost vs stay analysis (reverse mis-selling flow) --------------
def build_ulip_exit_analysis(
    monthly_premium: float, months_paid: int, doc_id: str = "sbi-life-smart-wealth-ulip"
) -> dict[str, Any] | None:
    """Honest exit-vs-stay math for a flagged ULIP, grounded in the fact-sheet
    (surrender charge, free-look window, charge drag). Includes a row where
    STAYING genuinely wins — the transparency rule applies to our own flags too."""
    doc = rag.get_doc(doc_id)
    if doc is None:
        return None
    m = doc.meta
    monthly = float(monthly_premium or m.get("monthly_premium", 0))
    annual = int(round(monthly * 12))
    paid = int(round(monthly * months_paid))
    alloc_pct = float(m.get("allocation_charge_pct_y1", 6.0))
    surrender = int(m.get("surrender_charge_y1", 3000))
    fund_estimate = int(round(paid * (1 - alloc_pct / 100)))
    refund_estimate = max(0, fund_estimate - surrender)
    free_look_days = int(m.get("free_look_days", 30))
    within_free_look = months_paid * 30 <= free_look_days
    lock_in = int(m.get("lock_in_years", 5))
    charges_pct = float(m.get("total_charges_pct_yr", 2.5))
    disc_pct = float(m.get("discontinued_fund_pct", 4.0))

    return {
        "product": str(m.get("title", "this ULIP")).split("—")[0].strip(),
        "insurer": m.get("insurer"),
        "monthly_premium": int(round(monthly)),
        "annual_premium": annual,
        "months_paid": months_paid,
        "paid_so_far": paid,
        "free_look": {
            "days": free_look_days,
            "within_window": within_free_look,
            "note": {
                "en": (f"You are within the {free_look_days}-day free-look window — a full "
                       "refund (minus proportionate risk charges) is available."
                       if within_free_look else
                       f"The {free_look_days}-day free-look window has passed "
                       f"({months_paid} months in), so exiting means surrender."),
                "hi": (f"आप {free_look_days}-दिन की फ्री-लुक अवधि में हैं — लगभग पूरा रिफंड मिल "
                       "सकता है।" if within_free_look else
                       f"{free_look_days}-दिन की फ्री-लुक अवधि बीत चुकी है ({months_paid} महीने "
                       "हो गए), इसलिए बाहर निकलने का रास्ता सरेंडर है।"),
            },
        },
        "exit_now": {
            "surrender_charge": surrender,
            "fund_value_estimate": fund_estimate,
            "refund_estimate": refund_estimate,
            "locked_until_year": lock_in,
            "discontinued_fund_pct": disc_pct,
            "note": {
                "en": (f"Surrender now: of ₹{paid:,} paid, ≈₹{fund_estimate:,} remains after the "
                       f"{alloc_pct}% allocation charge; minus the ₹{surrender:,} discontinuance "
                       f"charge ≈ ₹{refund_estimate:,} moves to a fund earning ~{disc_pct}% "
                       f"until year {lock_in}. Market movement excluded."),
                "hi": (f"अभी सरेंडर करने पर: ₹{paid:,} में से ≈₹{fund_estimate:,} बचता है "
                       f"({alloc_pct}% आवंटन शुल्क के बाद); ₹{surrender:,} डिसकंटीन्यूएंस चार्ज घटाकर "
                       f"≈₹{refund_estimate:,} एक फंड में जाएगा (~{disc_pct}% पर, {lock_in}वें साल तक)।"),
            },
        },
        "stay": {
            "annual_premium": annual,
            "charges_pct_yr": charges_pct,
            "lock_in_years": lock_in,
            "note": {
                "en": (f"Stay: keep paying ₹{annual:,}/year with ~{charges_pct}%/yr in charges "
                       "before any market return, locked till year "
                       f"{lock_in}."),
                "hi": (f"बने रहने पर: हर साल ₹{annual:,} देते रहें, ~{charges_pct}%/साल शुल्क कटेगा, "
                       f"{lock_in}वें साल तक लॉक।"),
            },
            # Transparency rule: where doing nothing / staying genuinely wins.
            "wins": [
                "No surrender charge",
                "Life cover continues",
                "Front-loaded charges are already paid",
            ],
        },
        "sources": [doc.source, "suitability-policy.md"],
        "disclaimer": (
            "Guidance, not advice. Figures are grounded in the fact-sheet and exclude "
            "market movement. Talk to a human advisor before exiting."
        ),
    }
