"""Tests for the six governance features:

  1. Reverse mis-selling detector (missold trigger + honest exit math)
  2. Devil's advocate (attach + suppress paths, rule-based)
  3. Attention budget (spend / exhaust / suppress)
  4. Guardian co-consent (gate + state machine)
  5. Hash-chained audit trail (append + verify + tamper detection)
  6. Do-nothing baseline (third comparison column, grounded)

Standalone: `python tests/test_new_features.py` (from /backend).
Budget / co-consent / audit tests run against a temp SQLite DB so they never
touch real demo state.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

import config  # noqa: E402
from engine import (  # noqa: E402
    agent,
    audit,
    coconsent,
    comparison,
    devils_advocate,
    feedback,
    triggers,
)
from models import TriggerType  # noqa: E402


@contextmanager
def temp_db():
    """Point the SQLite-backed stores at a throwaway file."""
    old = config.FEEDBACK_DB
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    config.FEEDBACK_DB = Path(path)
    try:
        yield Path(path)
    finally:
        config.FEEDBACK_DB = old
        try:
            os.unlink(path)
        except OSError:
            pass


def _data():
    data = json.loads((BACKEND / "data" / "transactions.json").read_text(encoding="utf-8"))
    return (data, datetime.fromisoformat(data["generated_at"]),
            {p["persona_id"]: p for p in data["personas"]})


# --- 1. Reverse mis-selling detector -----------------------------------------
def test_missold_trigger_fires_for_p6():
    data, now, metas = _data()
    meta = metas["p6_missold"]
    moments = triggers.detect_all_moments(meta, data["transactions"]["p6_missold"], now)
    missold = next((m for m in moments if m.trigger_type is TriggerType.MISSOLD_PRODUCT), None)
    assert missold is not None, "missold_product not detected for p6"
    e = missold.evidence
    assert e["monthly_premium"] == 2500
    assert e["months_paid"] >= 3
    assert e["income_pct"] and e["income_pct"] >= 15  # far over the 10% cap
    assert any("ULIP" in b or "auto-blocked" in b for b in e["suitability_blocks"])


def test_missold_agent_surfaces_flag_with_exit_math():
    data, now, metas = _data()
    meta = metas["p6_missold"]
    moments = [m.model_dump(mode="json")
               for m in triggers.detect_all_moments(meta, data["transactions"]["p6_missold"], now)]
    with temp_db():
        d = agent.run_agent_deterministic(meta, moments)
    assert d["action"] == "surface"
    assert d["flow"] == "missold"
    ex = d["exit_analysis"]
    assert ex is not None
    # Exit-vs-stay math grounded in the ULIP fact-sheet.
    assert ex["paid_so_far"] == ex["monthly_premium"] * ex["months_paid"]
    assert ex["exit_now"]["refund_estimate"] < ex["paid_so_far"]
    assert ex["exit_now"]["surrender_charge"] > 0
    assert ex["free_look"]["within_window"] is False  # 10 months in
    assert ex["stay"]["wins"], "transparency: a row where STAYING wins must exist"
    assert "sbi-life-smart-wealth-ulip.md" in ex["sources"]
    # Bilingual nudge with the flag framing.
    assert d["nudge"]["title"]["en"] and d["nudge"]["title"]["hi"]
    # Guardian co-consent gate attaches (assisted persona, ₹30k > ₹10k threshold).
    assert d["coconsent"]["required"] is True
    assert d["coconsent"]["amount"] == 30000


def test_other_personas_do_not_fire_missold():
    data, now, metas = _data()
    for pid in ("p1_idle_saver", "p2_premium_leaker", "p3_new_earner"):
        moments = triggers.detect_all_moments(metas[pid], data["transactions"][pid], now)
        assert TriggerType.MISSOLD_PRODUCT not in {m.trigger_type for m in moments}, pid


# --- 2. Devil's advocate ------------------------------------------------------
def test_devils_advocate_attaches_weak_objection():
    data, now, metas = _data()
    meta = metas["p2_premium_leaker"]
    moments = [m.model_dump(mode="json")
               for m in triggers.detect_all_moments(meta, data["transactions"]["p2_premium_leaker"], now)]
    with temp_db():
        d = agent.run_agent_deterministic(meta, moments)
    assert d["action"] == "surface"
    da = d["devils_advocate"]
    assert da["strength"] == "weak" and da["verdict"] == "attach"
    assert da["objection"]["en"] and da["objection"]["hi"]
    # Both sides visible in the decision log.
    assert any(s["step"] == "challenge" for s in d["decision_log"])
    assert any(s["step"] == "act" for s in d["decision_log"])


def test_devils_advocate_suppresses_low_value_cover():
    persona = {"persona_id": "_t_da_", "monthly_income": 30000}
    moment = {
        "trigger_type": "contextual_spend", "persona_id": "_t_da_",
        "title": "x", "summary": "x", "severity": "low",
        "suggested_category": "micro_cover",
        "evidence": {"merchant": "CROMA", "amount": 6000, "spend_kind": "electronics",
                     "cover_type": "damage & theft cover"},
        "evidence_txn_ids": [],
    }
    ch = devils_advocate.challenge(moment, persona)
    assert ch["strength"] == "strong" and ch["verdict"] == "suppress"
    with temp_db():
        d = agent.run_agent_deterministic(persona, [moment])
    assert d["action"] == "suppress"
    assert d["devils_advocate"]["verdict"] == "suppress"
    assert any(s["step"] == "challenge" for s in d["decision_log"])
    assert any("devil's advocate" in s["detail"].lower()
               for s in d["decision_log"] if s["step"] == "act")


def test_devils_advocate_small_idle_buffer_is_strong():
    ch = devils_advocate.challenge(
        {"trigger_type": "idle_balance", "evidence": {"idle_amount": 20000}},
        {"monthly_income": 60000},
    )
    assert ch["verdict"] == "suppress"  # likely the whole emergency buffer


# --- 3. Attention budget -------------------------------------------------------
def test_budget_spend_and_exhaust():
    with temp_db():
        pid = "_t_budget_"
        s = feedback.budget_status(pid)
        assert s == {"used": 0, "cap": 4, "remaining": 4, "month": s["month"]}
        for i in range(4):
            s = feedback.spend_budget(pid)
        assert s["used"] == 4 and s["remaining"] == 0
        # Reset clears the budget too (demo re-run).
        feedback.reset(pid)
        assert feedback.budget_status(pid)["remaining"] == 4


def test_budget_exhausted_suppresses_nudge():
    data, now, metas = _data()
    meta = metas["p2_premium_leaker"]
    moments = [m.model_dump(mode="json")
               for m in triggers.detect_all_moments(meta, data["transactions"]["p2_premium_leaker"], now)]
    with temp_db():
        for _ in range(4):
            feedback.spend_budget(meta["persona_id"])
        d = agent.run_agent_deterministic(meta, moments)
    assert d["action"] == "suppress"
    assert d.get("budget_suppressed") is True
    assert any("attention budget exhausted" in r for r in d["reason"])
    assert any(s["step"] == "budget" for s in d["decision_log"])


def test_budget_last_interruption_not_spent_on_low_value():
    persona = {"persona_id": "_t_budget2_", "monthly_income": 50000}
    moment = {
        "trigger_type": "contextual_spend", "persona_id": "_t_budget2_",
        "title": "x", "summary": "x", "severity": "low",
        "suggested_category": "micro_cover",
        "evidence": {"merchant": "MAKEMYTRIP", "amount": 18500, "spend_kind": "travel",
                     "cover_type": "trip protection"},
        "evidence_txn_ids": [],
    }
    with temp_db():
        for _ in range(3):
            feedback.spend_budget(persona["persona_id"])
        d = agent.run_agent_deterministic(persona, [moment])
    assert d["action"] == "suppress"
    assert any("not worth spending" in r for r in d["reason"])


def test_run_agent_wrapper_spends_only_on_surface():
    data, now, metas = _data()
    meta = metas["p1_idle_saver"]
    moments = [m.model_dump(mode="json")
               for m in triggers.detect_all_moments(meta, data["transactions"]["p1_idle_saver"], now)]
    old_key = config.ANTHROPIC_API_KEY
    config.ANTHROPIC_API_KEY = None  # force the deterministic engine
    try:
        with temp_db():
            d = agent.run_agent(meta, moments)
            assert d["action"] == "surface"
            assert d["attention_budget"]["used"] == 1  # surfaced → spent 1
            d2 = agent.run_agent(meta, moments, spend=False)  # sweep mode
            assert d2["attention_budget"]["used"] == 1  # unchanged
    finally:
        config.ANTHROPIC_API_KEY = old_key


# --- 4. Guardian co-consent -----------------------------------------------------
def test_coconsent_gate_thresholds():
    assisted = {"assisted_mode": True, "guardian": {"name": "R", "relation": "Son"}}
    assert coconsent.gate(assisted, 30000) is not None
    assert coconsent.gate(assisted, 5000) is None            # below threshold
    assert coconsent.gate({"monthly_income": 1}, 30000) is None  # not assisted
    g = coconsent.gate(assisted, 30000)
    assert g["required"] is True and g["note"]["en"] and g["note"]["hi"]


def test_coconsent_state_machine():
    with temp_db():
        rec = coconsent.request("_t_cc_", "ulip_exit_review", 30000,
                                guardian={"name": "R", "relation": "Son"})
        assert rec["status"] == "pending"
        got = coconsent.get(rec["id"])
        assert got["status"] == "pending"
        done = coconsent.decide(rec["id"], approve=True)
        assert done["status"] == "approved" and done["decided_ts"]
        # A decided request cannot be re-decided.
        try:
            coconsent.decide(rec["id"], approve=False)
            raise AssertionError("re-deciding an approved request must fail")
        except ValueError:
            pass
        # Decline path.
        rec2 = coconsent.request("_t_cc_", "open_sweep_fd", 40000)
        assert coconsent.decide(rec2["id"], approve=False)["status"] == "declined"
        # Unknown id.
        try:
            coconsent.decide("nope", approve=True)
            raise AssertionError("unknown request must fail")
        except ValueError:
            pass


# --- 5. Hash-chained audit trail --------------------------------------------------
def test_audit_append_and_verify_intact():
    with temp_db():
        r1 = audit.append("_t_p_", "premium_leak", "term_insurance", "surface",
                          {"suitability": {"suitable": True}})
        r2 = audit.append("_t_p_", "idle_balance", "fixed_deposit", "suppress",
                          {"reason": "budget"})
        assert r1["prev_hash"] == audit.GENESIS
        assert r2["prev_hash"] == r1["hash"]
        v = audit.verify()
        assert v["intact"] is True and v["records"] == 2 and v["broken_at"] is None


def test_audit_tamper_detected():
    with temp_db() as db:
        audit.append("_t_p_", "premium_leak", "term_insurance", "surface", {"n": 1})
        audit.append("_t_p_", "idle_balance", "fixed_deposit", "suppress", {"n": 2})
        audit.append("_t_p_", "salary_jump", "investment", "surface", {"n": 3})
        # Tamper with the middle record (a regulator's nightmare scenario).
        conn = sqlite3.connect(db)
        conn.execute("UPDATE audit_log SET action = 'surface' WHERE seq = 2")
        conn.commit()
        conn.close()
        v = audit.verify()
        assert v["intact"] is False and v["broken_at"] == 2


def test_audit_records_agent_decisions():
    data, now, metas = _data()
    meta = metas["p6_missold"]
    moments = [m.model_dump(mode="json")
               for m in triggers.detect_all_moments(meta, data["transactions"]["p6_missold"], now)]
    old_key = config.ANTHROPIC_API_KEY
    config.ANTHROPIC_API_KEY = None
    try:
        with temp_db():
            agent.run_agent(meta, moments)
            records = audit.chain()
            assert len(records) == 1
            rec = records[0]
            assert rec["persona_id"] == "p6_missold"
            assert rec["trigger_type"] == "missold_product"
            assert rec["action"] == "surface"
            assert rec["payload"]["suitability"]["suitable"] is False
            assert rec["payload"]["devils_advocate"]["verdict"] == "attach"
            assert audit.verify()["intact"] is True
    finally:
        config.ANTHROPIC_API_KEY = old_key


# --- 6. Do-nothing baseline ---------------------------------------------------------
def test_comparison_has_do_nothing_column():
    cmp = comparison.build_insurance_comparison("HDFC Life")
    assert cmp is not None
    assert all("do_nothing" in r for r in cmp["rows"])
    assert cmp["do_nothing_wins"], "honesty: doing nothing must win at least one row"
    assert any(r["winner"] == "do_nothing" for r in cmp["rows"])
    assert cmp["do_nothing_note"]
    # The cost of inaction is stated (5-year extra cost row).
    assert any(r["dimension"] == "Extra cost over 5 years" for r in cmp["rows"])


def test_do_nothing_idle_math_grounded():
    dn = comparison.build_do_nothing_idle(47000)
    assert dn is not None
    assert dn["source"] == "sbi-savings-account.md"
    # 47,000 × (6.0 − 2.7)% ≈ ₹1,551 of purchasing power lost per year.
    assert dn["yearly_real_loss"] == round(47000 * (dn["inflation_pct"] - dn["savings_rate_pct"]) / 100)
    assert dn["detail"]["en"] and dn["detail"]["hi"]


def test_idle_flow_carries_do_nothing_payload():
    data, now, metas = _data()
    meta = metas["p1_idle_saver"]
    moments = [m.model_dump(mode="json")
               for m in triggers.detect_all_moments(meta, data["transactions"]["p1_idle_saver"], now)]
    with temp_db():
        d = agent.run_agent_deterministic(meta, moments)
    assert d["action"] == "surface"
    assert d["do_nothing"]["yearly_real_loss"] > 0


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
