"""Subscription Saver trigger — recurring-charge clustering + renewal reminder.

The bank-native advantage: many subscriptions run on UPI AutoPay / e-mandates,
which SBI sees *at source* (unlike third-party trackers that screen-scrape). So
for mandate-based subs we can offer an in-app pause/stop (mocked). We never claim
to auto-cancel a third-party service — cancellation is guided only.

Honesty note: the bank can see the mandate and its *next charge date*, but NOT
whether the user opened the third-party app. So we never assert "you haven't
used this" — we give a gentle reminder a few days before renewal and let the
user decide. Nothing here claims a usage signal we can't observe.
"""
from __future__ import annotations

from typing import Any

from engine import rag
from models import AdoptionMoment, TriggerType

# Remind this many days before a charge — early enough to pause/cancel in time.
RENEWAL_REMINDER_DAYS = 3


def _category_map() -> dict[str, str]:
    doc = next((d for d in rag.docs_by_type("payee_category_map")), None)
    raw = (doc.meta.get("map") if doc else None) or {}
    return {str(k).upper(): str(v) for k, v in raw.items()}


def detect(persona: dict[str, Any]) -> AdoptionMoment | None:
    subs = persona.get("subscriptions") or []
    if not subs:
        return None

    cat_map = _category_map()
    enriched = []
    for s in subs:
        enriched.append(
            {
                **s,
                "category": s.get("category") or cat_map.get(str(s.get("name", "")).upper(), "OTHER"),
                "is_mandate": str(s.get("via", "")).upper().startswith("UPI_AUTOPAY"),
            }
        )

    total_monthly = sum(s["amount"] for s in enriched)
    # Gentle reminder window: surface the subscription(s) renewing within N days,
    # purely off the observable next-charge date. No usage claim.
    upcoming = sorted(
        [s for s in enriched if s.get("next_charge_in_days", 99) <= RENEWAL_REMINDER_DAYS],
        key=lambda s: s.get("next_charge_in_days", 99),
    )
    if not upcoming:
        return None
    headline = upcoming[0]
    days = headline.get("next_charge_in_days")

    return AdoptionMoment(
        trigger_type=TriggerType.SUBSCRIPTION_SAVER,
        persona_id=persona["persona_id"],
        title="A subscription renews soon",
        summary=(
            f"{headline['name'].title()} (₹{headline['amount']:,}/mo) renews in {days} days. "
            "If you're not using it, you can pause it before the charge."
        ),
        severity="high",
        suggested_category="subscription_review",
        evidence={
            "subscriptions": enriched,
            "flagged": headline,
            "renews_in_days": days,
            "total_monthly": total_monthly,
            # Conditional: what you'd save IF you choose to pause this one.
            "potential_savings": headline["amount"],
            "is_mandate": headline.get("is_mandate", False),
        },
        evidence_txn_ids=[],
    )
