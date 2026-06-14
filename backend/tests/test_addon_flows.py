"""Flow D (feature discovery) + Subscription Saver + ladder/goal checks.

Standalone: `python tests/test_addon_flows.py` (from /backend).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from engine import agent, triggers, adoption_ladder, goal_engine  # noqa: E402


def _data():
    data = json.loads((BACKEND / "data" / "transactions.json").read_text(encoding="utf-8"))
    return data, datetime.fromisoformat(data["generated_at"]), {p["persona_id"]: p for p in data["personas"]}


def test_explorer_surfaces_feature_discovery_over_idle():
    data, now, metas = _data()
    meta = metas["p4_explorer"]
    moments = [m.model_dump(mode="json") for m in triggers.detect_all_moments(meta, data["transactions"]["p4_explorer"], now)]
    d = agent.run_agent_deterministic(meta, moments)
    assert d["action"] == "surface"
    assert d["surfaced_moment"]["trigger_type"] == "feature_discovery"
    assert d["flow"] == "feature_discovery"
    assert d["walkthrough"]["feature"] == "bill_pay"
    assert len(d["walkthrough"]["steps"]) >= 3
    # idle should have been a candidate but suppressed in favour of platform adoption
    assert any(s["trigger_type"] == "idle_balance" for s in d["suppressed"])


def test_subscription_saver_flags_unused_and_redirects_to_goal():
    data, now, metas = _data()
    meta = metas["p5_subscription_saver"]
    moments = [m.model_dump(mode="json") for m in triggers.detect_all_moments(meta, data["transactions"]["p5_subscription_saver"], now)]
    d = agent.run_agent_deterministic(meta, moments)
    assert d["surfaced_moment"]["trigger_type"] == "subscription_saver"
    assert d["flagged"]["name"] == "CULT FIT"
    assert d["is_mandate"] is True
    assert d["goal_redirect"] is not None
    assert d["goal_redirect"]["pct_after"] > d["goal_redirect"]["pct_before"]


def test_adoption_ladder_advances():
    assert adoption_ladder.next_after("bill_pay") == "autopay"
    assert adoption_ladder.next_after("autopay") == "credit_score"
    st = adoption_ladder.state({"bill_pay"})
    assert st["next"] == "autopay"
    assert any(rung["feature"] == "bill_pay" and rung["adopted"] for rung in st["ladder"])


def test_goal_redirect_math():
    goal = {"goal_id": "g1", "label": "Buy a bike", "target_amount": 120000, "saved_so_far": 38000}
    r = goal_engine.frame_redirect(goal, 1300)
    assert r["pct_before"] == 32 and r["pct_after"] == 33
    assert "Buy a bike" in r["text"]["en"]


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
