"""Flow D trigger — feature blind-spot detection (platform adoption).

Fires when BOTH hold:
  1. Narrow-usage signal: the user's recent YONO actions ⊆ {upi, balance_check}
  2. Relevance signal: a specific unused YONO feature is evidenced by behaviour
     (e.g. a recurring electricity bill leaving to a non-YONO app → Bill Pay).

Unlike a static tooltip that shows everyone the same hint, this points at the
ONE feature this user already needs but has never opened in YONO.
"""
from __future__ import annotations

from typing import Any

from engine import rag
from models import AdoptionMoment, TriggerType

NARROW_USAGE = {"upi", "balance_check"}


def _feature_doc(feature: str) -> rag.Doc | None:
    return next(
        (d for d in rag.docs_by_type("yono_feature") if d.meta.get("feature") == feature),
        None,
    )


def detect(persona: dict[str, Any]) -> AdoptionMoment | None:
    actions = set(persona.get("yono_actions_30d") or [])
    used = set(persona.get("features_ever_used") or [])
    external = persona.get("external_recurring") or []
    if not actions or not external:
        return None

    # 1. Narrow usage: nothing beyond UPI + balance check.
    if not actions.issubset(NARROW_USAGE):
        return None

    # 2. Relevance: pick the strongest evidenced unused feature.
    for item in external:
        feature = item.get("feature")
        if not feature or feature in used:
            continue
        doc = _feature_doc(feature)
        if doc is None:
            continue
        meta = doc.meta
        display = meta.get("display_name", feature.replace("_", " ").title())
        secs = meta.get("time_seconds", 30)
        return AdoptionMoment(
            trigger_type=TriggerType.FEATURE_DISCOVERY,
            persona_id=persona["persona_id"],
            title=f"A YONO feature you've never used: {display}",
            summary=(
                f"You pay {item.get('payee', 'this bill').title()} every month using "
                f"{item.get('via', 'another app')}. YONO can do this in under {secs} "
                "seconds. Want me to show you?"
            ),
            severity="medium",
            suggested_category="feature_discovery",
            evidence={
                "feature": feature,
                "display_name": display,
                "external_payee": item.get("payee"),
                "via": item.get("via"),
                "amount": item.get("amount"),
                "time_seconds": secs,
                "steps": meta.get("steps", []),
                "unlocks": meta.get("unlocks"),
                "doc_id": doc.id,
            },
            evidence_txn_ids=[],
        )
    return None
