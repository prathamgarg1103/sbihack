"""Hard-rule checks for the suitability filter.

Runs under pytest, or standalone: `python tests/test_suitability.py` (from /backend).
"""
from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from engine.suitability import check_suitability  # noqa: E402

PERSONA = {"monthly_income": 46000}


def test_term_insurance_is_suitable():
    r = check_suitability(product_type="term_insurance", monthly_cost=983, persona=PERSONA)
    assert r["suitable"] is True
    assert r["blocks"] == []


def test_ulip_is_always_blocked():
    r = check_suitability(product_type="ulip", monthly_cost=500, persona=PERSONA)
    assert r["suitable"] is False
    assert any("auto-blocked" in b for b in r["blocks"])


def test_ulip_blocked_even_when_cheap_and_asked():
    # Cheap + within budget must NOT rescue a blocked product type.
    r = check_suitability(product_type="ULIP", monthly_cost=1, persona={"monthly_income": 999999})
    assert r["suitable"] is False


def test_over_budget_premium_blocked():
    # 10k/mo premium on 46k income is ~22% -> over the 10% cap.
    r = check_suitability(product_type="term_insurance", monthly_cost=10000, persona=PERSONA)
    assert r["suitable"] is False
    assert any("over budget" in b for b in r["blocks"])


def test_recently_skipped_suppressed():
    r = check_suitability(
        product_type="fixed_deposit", monthly_cost=0, persona=PERSONA, recently_skipped=True
    )
    assert r["suitable"] is False
    assert any("skipped" in b for b in r["blocks"])


def test_fixed_deposit_no_income_still_ok():
    r = check_suitability(product_type="fixed_deposit", monthly_cost=0, persona={})
    assert r["suitable"] is True


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
