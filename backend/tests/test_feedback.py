"""Feedback store + learn-loop checks.

Runs under pytest, or standalone: `python tests/test_feedback.py` (from /backend).
Uses an isolated persona id so it never touches real demo state.
"""
from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from engine import feedback  # noqa: E402

PID = "_test_persona_"


def _clean():
    feedback.reset(PID)


def test_record_and_read_skip():
    _clean()
    assert feedback.skipped_categories(PID) == set()
    feedback.record(PID, "idle_balance", "skipped")
    assert "idle_balance" in feedback.skipped_categories(PID)
    _clean()


def test_adopted_is_not_a_skip():
    _clean()
    feedback.record(PID, "premium_leak", "adopted")
    assert feedback.skipped_categories(PID) == set()
    _clean()


def test_summary_counts():
    _clean()
    feedback.record(PID, "idle_balance", "skipped")
    feedback.record(PID, "premium_leak", "adopted")
    feedback.record(PID, "premium_leak", "adopted")
    s = feedback.summary(PID)
    assert s.get("skipped") == 1 and s.get("adopted") == 2
    _clean()


def test_invalid_outcome_rejected():
    try:
        feedback.record(PID, "idle_balance", "bogus")
    except ValueError:
        return
    raise AssertionError("invalid outcome should raise ValueError")


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
