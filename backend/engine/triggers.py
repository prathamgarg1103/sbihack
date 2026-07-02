"""Trigger engine — the 'perceive + detect moment' stage of the agent loop.

Consumes a persona's synthetic transaction stream, classifies payees, and runs
rule + threshold detection to emit candidate `AdoptionMoment`s. It does NOT
decide whether to nudge — that's the agent core's job (M5). It only surfaces
opportunities, with the evidence attached so every later step stays grounded.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from statistics import mean
from typing import Any

from models import AdoptionMoment, PayeeCategory, TriggerType

# --- Tunable thresholds (the feedback loop in M8 will nudge these) ---------
IDLE_MIN_BALANCE = 25_000          # only flag idle cash above this floor
IDLE_MIN_DAYS = 60                 # must have sat this long
SALARY_JUMP_PCT = 0.20             # >=20% month-over-month rise counts as a jump
RECURRING_MIN_HITS = 3             # N occurrences to call a debit "recurring"
RECURRING_AMOUNT_TOLERANCE = 0.06  # amounts within +/-6% are "the same" payment
CONTEXTUAL_MIN_AMOUNT = 5_000      # contextual spend must be at least this big
CONTEXTUAL_WINDOW_DAYS = 30        # ...and this recent

# --- Payee classification dictionaries -------------------------------------
_SALARY_HINTS = ("SALARY", "PAYROLL", "WAGES", "PENSION")
_PREMIUM_HINTS = (
    "LIFE", "INSURANCE", "PREMIUM", "ASSURANCE", "POLICY",
    "PRU", "AIA", "ALLIANZ", "MAX LIFE", "TERM PLAN",
)
_BILL_HINTS = (
    "ELECTRICITY", "RECHARGE", "BILL", "GAS", "WATER", "BROADBAND",
    "BESCOM", "JIO", "AIRTEL", "DTH", "POSTPAID",
)
_TRANSFER_HINTS = (
    "SELF", "TRANSFER", "A/C", "OPENING BALANCE", "RENT", "NEFT", "IMPS TO",
)

# Known insurers -> display name. Anything without "SBI" is a competitor leak.
_INSURER_DISPLAY = {
    "HDFC LIFE": "HDFC Life",
    "ICICI PRU": "ICICI Prudential Life",
    "MAX LIFE": "Max Life",
    "BAJAJ ALLIANZ": "Bajaj Allianz Life",
    "TATA AIA": "Tata AIA Life",
    "LIC": "LIC",
    "KOTAK LIFE": "Kotak Life",
}

# Merchants that imply a contextual cover opportunity.
_TRAVEL_MERCHANTS = ("MAKEMYTRIP", "GOIBIBO", "IRCTC", "YATRA", "CLEARTRIP", "EASEMYTRIP")
_ELECTRONICS_MERCHANTS = ("CROMA", "RELIANCE DIGITAL", "VIJAY SALES", "IMAGINE")


def classify_payee(payee_name: str) -> PayeeCategory:
    """Rule-based payee classifier (upgrade path: embedding cosine to prototypes)."""
    name = payee_name.upper()
    if any(h in name for h in _SALARY_HINTS):
        return PayeeCategory.SALARY
    if any(h in name for h in _PREMIUM_HINTS):
        return PayeeCategory.PREMIUM
    if any(h in name for h in _TRANSFER_HINTS):
        return PayeeCategory.TRANSFER
    if any(h in name for h in _BILL_HINTS):
        return PayeeCategory.BILL
    return PayeeCategory.MERCHANT


def _insurer_display(payee_name: str) -> str:
    upper = payee_name.upper()
    for key, disp in _INSURER_DISPLAY.items():
        if key in upper:
            return disp
    # Fallback: strip the word PREMIUM and title-case.
    return upper.replace("PREMIUM", "").strip().title() or payee_name.title()


def _is_competitor_insurer(payee_name: str) -> bool:
    return "SBI" not in payee_name.upper()


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def _days_between(later: datetime, earlier: datetime) -> int:
    return max(0, (later - earlier).days)


# --- Individual detectors ---------------------------------------------------
def detect_idle_balance(persona_id: str, txns: list[dict], now: datetime) -> AdoptionMoment | None:
    """Flow A: a meaningful balance has sat untouched for a long stretch."""
    if not txns:
        return None
    ordered = sorted(txns, key=lambda r: r["timestamp"])
    window = [r for r in ordered if _days_between(now, _parse(r["timestamp"])) <= 90]
    if not window:
        return None

    floor = min(r["balance_after"] for r in window)
    if floor < IDLE_MIN_BALANCE:
        return None

    # Guard: "idle" means a parked buffer, not recently-arrived income that is
    # still accumulating. If the balance is in a strong upward trend across the
    # window, this is active money (e.g. a new earner) — not a sweep-FD moment.
    start_balance = window[0]["balance_after"]
    end_balance = window[-1]["balance_after"]
    if end_balance - start_balance > floor * 0.5:
        return None

    # How long has the balance continuously stayed at/above this floor?
    last_dip = None
    for r in ordered:
        if r["balance_after"] < floor:
            last_dip = _parse(r["timestamp"])
    anchor = last_dip if last_dip else _parse(ordered[0]["timestamp"])
    days_idle = _days_between(now, anchor)
    if days_idle < IDLE_MIN_DAYS:
        return None

    idle_amount = int(floor // 1000 * 1000)  # round down to a clean figure
    return AdoptionMoment(
        trigger_type=TriggerType.IDLE_BALANCE,
        persona_id=persona_id,
        title="Idle savings detected",
        summary=(
            f"About ₹{idle_amount:,} has stayed idle in your savings account for "
            f"{days_idle}+ days, earning only 2.70% p.a."
        ),
        severity="medium",
        suggested_category="fixed_deposit",
        evidence={
            "idle_amount": idle_amount,
            "days_idle": days_idle,
            "savings_rate_pct": 2.70,
        },
        evidence_txn_ids=[window[0]["txn_id"], window[-1]["txn_id"]],
    )


def detect_premium_leak(persona_id: str, txns: list[dict], now: datetime) -> AdoptionMoment | None:
    """Flow B (hero): a recurring premium leaking to a competitor insurer."""
    by_payee: dict[str, list[dict]] = defaultdict(list)
    for r in txns:
        if r["amount"] < 0 and classify_payee(r["payee_name"]) is PayeeCategory.PREMIUM:
            by_payee[r["payee_name"]].append(r)

    for payee, rows in by_payee.items():
        if len(rows) < RECURRING_MIN_HITS or not _is_competitor_insurer(payee):
            continue
        amounts = [abs(r["amount"]) for r in rows]
        avg = mean(amounts)
        if avg <= 0:
            continue
        spread = (max(amounts) - min(amounts)) / avg
        if spread > RECURRING_AMOUNT_TOLERANCE:
            continue  # not a stable recurring payment

        monthly = round(avg)
        annual = monthly * 12
        return AdoptionMoment(
            trigger_type=TriggerType.PREMIUM_LEAK,
            persona_id=persona_id,
            title="Recurring premium to another insurer",
            summary=(
                f"You pay about ₹{monthly:,}/month (₹{annual:,}/year) to "
                f"{_insurer_display(payee)}. Want an honest side-by-side comparison?"
            ),
            severity="high",
            suggested_category="insurance_compare",
            evidence={
                "competitor": _insurer_display(payee),
                "raw_payee": payee,
                "monthly_premium": monthly,
                "annual_premium": annual,
                "occurrences": len(rows),
            },
            evidence_txn_ids=[r["txn_id"] for r in rows[-3:]],
        )
    return None


def _monthly_salary(txns: list[dict]) -> list[tuple[str, float]]:
    """Total salary credited per calendar month, oldest first."""
    buckets: dict[str, float] = defaultdict(float)
    for r in txns:
        if r["amount"] > 0 and classify_payee(r["payee_name"]) is PayeeCategory.SALARY:
            key = _parse(r["timestamp"]).strftime("%Y-%m")
            buckets[key] += r["amount"]
    return sorted(buckets.items())


def detect_salary_jump(persona_id: str, txns: list[dict], now: datetime) -> AdoptionMoment | None:
    """Flow C (part 1): a recent step-up in monthly salary."""
    months = _monthly_salary(txns)
    if len(months) < 2:
        return None
    # Find the largest month-over-month step-up across the series (the jump may
    # have happened a couple of months ago and then held steady).
    best_rise = 0.0
    prev_amt = latest_amt = 0.0
    for (_, a), (_, b) in zip(months, months[1:]):
        if a <= 0:
            continue
        rise = (b - a) / a
        if rise > best_rise:
            best_rise, prev_amt, latest_amt = rise, a, b
    if best_rise < SALARY_JUMP_PCT:
        return None
    rise = best_rise

    return AdoptionMoment(
        trigger_type=TriggerType.SALARY_JUMP,
        persona_id=persona_id,
        title="Income just went up",
        summary=(
            f"Your salary rose from ₹{int(prev_amt):,} to ₹{int(latest_amt):,} "
            f"(+{round(rise * 100)}%). A good moment to start investing — across the "
            "whole market, honestly."
        ),
        severity="medium",
        suggested_category="invest_shelf",
        evidence={
            "previous_salary": int(prev_amt),
            "latest_salary": int(latest_amt),
            "increase_pct": round(rise * 100),
        },
        evidence_txn_ids=[],
    )


def detect_contextual_spend(persona_id: str, txns: list[dict], now: datetime) -> AdoptionMoment | None:
    """Flow C (part 2): a recent travel/electronics spend = a cover moment."""
    best: dict[str, Any] | None = None
    for r in txns:
        if r["amount"] >= 0:
            continue
        if _days_between(now, _parse(r["timestamp"])) > CONTEXTUAL_WINDOW_DAYS:
            continue
        amount = abs(r["amount"])
        if amount < CONTEXTUAL_MIN_AMOUNT:
            continue
        name = r["payee_name"].upper()
        if any(m in name for m in _TRAVEL_MERCHANTS):
            kind = "travel"
        elif any(m in name for m in _ELECTRONICS_MERCHANTS):
            kind = "electronics"
        else:
            continue
        if best is None or amount > best["amount"]:
            best = {"row": r, "amount": amount, "kind": kind}

    if best is None:
        return None

    kind = best["kind"]
    amount = int(best["amount"])
    cover = "trip protection" if kind == "travel" else "damage & theft cover"
    return AdoptionMoment(
        trigger_type=TriggerType.CONTEXTUAL_SPEND,
        persona_id=persona_id,
        title=f"Recent {kind} purchase",
        summary=(
            f"You spent ₹{amount:,} on {best['row']['payee_name'].title()}. "
            f"Want optional {cover} for it?"
        ),
        severity="low",
        suggested_category="micro_cover",
        evidence={
            "merchant": best["row"]["payee_name"],
            "amount": amount,
            "spend_kind": kind,
            "cover_type": cover,
        },
        evidence_txn_ids=[best["row"]["txn_id"]],
    )


def detect_missold_product(persona: dict, txns: list[dict], now: datetime) -> AdoptionMoment | None:
    """Reverse mis-selling (hero): a recurring premium for a product the user
    ALREADY OWNS that fails the suitability filter — canonically a ULIP sold to
    a low/fixed-income user. Diya flags the bank's own past sale instead of
    hiding it. Numbers are grounded in the ULIP fact-sheet corpus doc."""
    from engine import rag, suitability

    ulip_docs = rag.docs_by_type("ulip_factsheet")
    if not ulip_docs:
        return None

    by_payee: dict[str, list[dict]] = defaultdict(list)
    for r in txns:
        if r["amount"] < 0 and classify_payee(r["payee_name"]) is PayeeCategory.PREMIUM:
            by_payee[r["payee_name"]].append(r)

    for payee, rows in by_payee.items():
        if len(rows) < RECURRING_MIN_HITS:
            continue
        upper = payee.upper()
        doc = next(
            (d for d in ulip_docs
             if "ULIP" in upper or str(d.meta.get("payee_hint", "")).upper() in upper),
            None,
        )
        if doc is None:
            continue
        amounts = [abs(r["amount"]) for r in rows]
        avg = mean(amounts)
        if avg <= 0 or (max(amounts) - min(amounts)) / avg > RECURRING_AMOUNT_TOLERANCE:
            continue

        monthly = round(avg)
        annual = monthly * 12
        fit = suitability.check_suitability(
            product_type="ulip", monthly_cost=monthly, persona=persona
        )
        if fit["suitable"]:
            continue  # only flag holdings that fail today's rules

        income = float(persona.get("monthly_income", 0) or 0)
        income_pct = round(monthly / income * 100) if income else None
        title = str(doc.meta.get("title", "this policy")).split("—")[0].strip()
        return AdoptionMoment(
            trigger_type=TriggerType.MISSOLD_PRODUCT,
            persona_id=persona["persona_id"],
            title="A policy you hold looks unsuitable for you",
            summary=(
                f"You pay ₹{monthly:,}/month for {title} — a ULIP. It fails the "
                "suitability rules we apply today. You may have exit options."
            ),
            severity="high",
            suggested_category="missold_review",
            evidence={
                "product": title,
                "doc_id": doc.id,
                "raw_payee": payee,
                "monthly_premium": monthly,
                "annual_premium": annual,
                "months_paid": len(rows),
                "paid_so_far": monthly * len(rows),
                "income_pct": income_pct,
                "suitability_blocks": fit["blocks"],
            },
            evidence_txn_ids=[r["txn_id"] for r in rows[-3:]],
        )
    return None


_DETECTORS = (
    detect_idle_balance,
    detect_premium_leak,
    detect_salary_jump,
    detect_contextual_spend,
)


def detect_all(persona_id: str, txns: list[dict], now: datetime) -> list[AdoptionMoment]:
    """Run every transaction-based detector; return all candidate moments (0..N)."""
    moments = []
    for detect in _DETECTORS:
        moment = detect(persona_id, txns, now)
        if moment is not None:
            moments.append(moment)
    return moments


def detect_all_moments(
    persona: dict, txns: list[dict], now: datetime
) -> list[AdoptionMoment]:
    """All candidate moments: transaction-based + platform/engagement detectors
    (feature blind-spot, subscriptions) that read the persona's structured
    signals. Imported lazily to avoid a circular import at module load."""
    from engine import feature_blindspot, subscription_detector

    moments = detect_all(persona["persona_id"], txns, now)
    missold = detect_missold_product(persona, txns, now)
    if missold is not None:
        moments.append(missold)
    for meta_detect in (feature_blindspot.detect, subscription_detector.detect):
        moment = meta_detect(persona)
        if moment is not None:
            moments.append(moment)
    return moments
