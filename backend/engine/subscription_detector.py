"""Subscription Saver trigger — recurring-charge clustering + unused/renewal flags.

The bank-native advantage: many subscriptions run on UPI AutoPay / e-mandates,
which SBI sees *at source* (unlike third-party trackers that screen-scrape). So
for mandate-based subs we can offer an in-app pause/stop (mocked). We never claim
to auto-cancel a third-party service — cancellation is guided only.
"""
from __future__ import annotations

from typing import Any

from engine import rag
from models import AdoptionMoment, TriggerType

RENEWAL_SOON_DAYS = 4


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
    unused = [s for s in enriched if not s.get("used_last_30d", True)]
    # The headline: an unused subscription whose renewal is imminent.
    flagged = sorted(
        [s for s in unused if s.get("next_charge_in_days", 99) <= RENEWAL_SOON_DAYS],
        key=lambda s: s.get("next_charge_in_days", 99),
    )
    headline = flagged[0] if flagged else (unused[0] if unused else None)
    if headline is None:
        return None

    potential_savings = sum(s["amount"] for s in unused)
    soon = headline.get("next_charge_in_days")
    renew_txt = f"renews in {soon} days" if soon is not None else "is unused"
    return AdoptionMoment(
        trigger_type=TriggerType.SUBSCRIPTION_SAVER,
        persona_id=persona["persona_id"],
        title="Unused subscription about to renew",
        summary=(
            f"{headline['name'].title()} (₹{headline['amount']:,}/mo) {renew_txt} and you "
            f"haven't used it in 30 days. Review your {len(enriched)} subscriptions?"
        ),
        severity="high" if flagged else "medium",
        suggested_category="subscription_review",
        evidence={
            "subscriptions": enriched,
            "flagged": headline,
            "unused_count": len(unused),
            "total_monthly": total_monthly,
            "potential_savings": potential_savings,
            "is_mandate": headline.get("is_mandate", False),
        },
        evidence_txn_ids=[],
    )
