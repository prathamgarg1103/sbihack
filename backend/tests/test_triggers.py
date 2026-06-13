"""Unit + integration checks for the trigger engine.

Runs under pytest, or standalone: `python tests/test_triggers.py` (from /backend).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

# Make /backend importable when run as a plain script.
BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from engine import triggers  # noqa: E402
from models import PayeeCategory, TriggerType  # noqa: E402


def _load():
    path = BACKEND / "data" / "transactions.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data, datetime.fromisoformat(data["generated_at"])


def test_classifier_matches_ground_truth():
    """The rule-based classifier should agree with the synthetic truth labels
    on the vast majority of payees (it never saw the labels)."""
    data, _ = _load()
    total = hits = 0
    misses: list[tuple[str, str, str]] = []
    for rows in data["transactions"].values():
        for r in rows:
            total += 1
            predicted = triggers.classify_payee(r["payee_name"]).value
            if predicted == r["payee_category_truth"]:
                hits += 1
            else:
                misses.append((r["payee_name"], r["payee_category_truth"], predicted))
    accuracy = hits / total
    assert accuracy >= 0.95, f"classifier accuracy {accuracy:.2%}; misses={misses[:8]}"


def test_classifier_units():
    assert triggers.classify_payee("HDFC LIFE PREMIUM") is PayeeCategory.PREMIUM
    assert triggers.classify_payee("INFOSYS LTD SALARY") is PayeeCategory.SALARY
    assert triggers.classify_payee("JIO RECHARGE") is PayeeCategory.BILL
    assert triggers.classify_payee("SELF A/C 5521 TRANSFER") is PayeeCategory.TRANSFER
    assert triggers.classify_payee("ZOMATO") is PayeeCategory.MERCHANT


def test_idle_saver_fires_idle_balance():
    data, now = _load()
    moments = triggers.detect_all("p1_idle_saver", data["transactions"]["p1_idle_saver"], now)
    kinds = {m.trigger_type for m in moments}
    assert TriggerType.IDLE_BALANCE in kinds
    idle = next(m for m in moments if m.trigger_type is TriggerType.IDLE_BALANCE)
    assert idle.evidence["idle_amount"] >= 40_000
    assert idle.evidence["days_idle"] >= 60


def test_premium_leaker_fires_leak():
    data, now = _load()
    moments = triggers.detect_all("p2_premium_leaker", data["transactions"]["p2_premium_leaker"], now)
    leak = next((m for m in moments if m.trigger_type is TriggerType.PREMIUM_LEAK), None)
    assert leak is not None, "premium leak not detected"
    assert leak.evidence["monthly_premium"] == 1240
    assert "HDFC Life" in leak.evidence["competitor"]
    assert leak.evidence["occurrences"] >= 3


def test_new_earner_fires_salary_and_contextual():
    data, now = _load()
    moments = triggers.detect_all("p3_new_earner", data["transactions"]["p3_new_earner"], now)
    kinds = {m.trigger_type for m in moments}
    assert TriggerType.SALARY_JUMP in kinds
    assert TriggerType.CONTEXTUAL_SPEND in kinds
    jump = next(m for m in moments if m.trigger_type is TriggerType.SALARY_JUMP)
    assert jump.evidence["previous_salary"] == 35_000
    assert jump.evidence["latest_salary"] == 55_000
    ctx = next(m for m in moments if m.trigger_type is TriggerType.CONTEXTUAL_SPEND)
    assert ctx.evidence["spend_kind"] == "travel"


def test_idle_saver_has_no_premium_leak():
    """Negative case: the idle saver should NOT trip the premium-leak detector."""
    data, now = _load()
    moments = triggers.detect_all("p1_idle_saver", data["transactions"]["p1_idle_saver"], now)
    assert TriggerType.PREMIUM_LEAK not in {m.trigger_type for m in moments}


def test_new_earner_balance_not_flagged_idle():
    """Negative case: actively-accumulating income must not read as 'idle'."""
    data, now = _load()
    moments = triggers.detect_all("p3_new_earner", data["transactions"]["p3_new_earner"], now)
    assert TriggerType.IDLE_BALANCE not in {m.trigger_type for m in moments}


def _run_standalone() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_run_standalone())
