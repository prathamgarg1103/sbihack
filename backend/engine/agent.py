"""Agent core — the perceive → reason → act loop.

Given a persona's detected moments, the agent decides WHETHER to interrupt,
which product fits, whether it passes suitability, and what the (bilingual)
nudge should say — logging every step so the autonomy is visible.

Two execution paths, same observable contract:
  * **LLM path** (when ANTHROPIC_API_KEY is set): a real Anthropic tool-calling
    loop. Tools: query_rag, check_suitability, build_comparison. Wrapped so any
    failure degrades to the deterministic path rather than breaking the demo.
  * **Deterministic path** (no key): rule-based orchestration that calls the
    SAME tools and emits the same decision-log shape, with pre-authored EN/हिंदी
    copy. This is what runs in the offline demo.

Both return the same `AgentDecision` dict, so the frontend never knows or cares
which ran (other than the `engine` field, shown for transparency).
"""
from __future__ import annotations

from typing import Any

import config
from engine import comparison, rag, suitability

# Highest-value first — the agent surfaces one and suppresses the rest.
PRIORITY = ["premium_leak", "idle_balance", "contextual_spend", "salary_jump"]


# --- Product mapping (what the trigger should be answered with) -------------
def _product_for(moment: dict[str, Any]) -> dict[str, Any]:
    cat = moment["suggested_category"]
    ev = moment.get("evidence", {})
    if cat == "fixed_deposit":
        doc = rag.get_doc("sbi-fd-sweep")
        return {"type": "fixed_deposit", "monthly_cost": 0, "doc_id": "sbi-fd-sweep", "doc": doc}
    if cat == "insurance_compare":
        doc = rag.get_doc("sbi-life-eshield")
        cost = doc.meta.get("monthly_premium", 0) if doc else 0
        return {"type": "term_insurance", "monthly_cost": cost, "doc_id": "sbi-life-eshield", "doc": doc}
    if cat == "micro_cover":
        kind = str(ev.get("spend_kind", ""))
        if kind == "electronics":
            doc = rag.get_doc("sbi-general-device")
            return {"type": "device_insurance", "monthly_cost": 0,
                    "doc_id": "sbi-general-device", "doc": doc}
        doc = rag.get_doc("sbi-general-travel")
        return {"type": "travel_insurance", "monthly_cost": 0,
                "doc_id": "sbi-general-travel", "doc": doc}
    return {"type": "unknown", "monthly_cost": 0, "doc_id": None, "doc": None}


# --- Bilingual copy (grounded numbers interpolated into EN/हिंदी templates) --
def _rupee(n: Any) -> str:
    try:
        return f"{int(round(float(n))):,}"
    except (TypeError, ValueError):
        return str(n)


def _bilingual(moment: dict[str, Any]) -> dict[str, dict[str, str]]:
    t = moment["trigger_type"]
    e = moment.get("evidence", {})
    if t == "premium_leak":
        comp = e.get("competitor", "another insurer")
        m = _rupee(e.get("monthly_premium"))
        y = _rupee(e.get("annual_premium"))
        return {
            "title": {"en": "Recurring premium to another insurer",
                      "hi": "किसी और बीमा कंपनी को हर महीने प्रीमियम"},
            "body": {
                "en": f"You pay about ₹{m}/month (₹{y}/year) to {comp}. "
                      "Want an honest side-by-side comparison?",
                "hi": f"आप हर महीने लगभग ₹{m} (₹{y}/साल) {comp} को देते हैं। "
                      "क्या आप एक ईमानदार तुलना देखना चाहेंगे?",
            },
            "cta": {"en": "See the honest comparison", "hi": "ईमानदार तुलना देखें"},
        }
    if t == "idle_balance":
        amt = _rupee(e.get("idle_amount"))
        days = e.get("days_idle")
        rate = e.get("savings_rate_pct")
        return {
            "title": {"en": "Idle savings detected", "hi": "बचत खाते में पैसा बिना इस्तेमाल पड़ा है"},
            "body": {
                "en": f"About ₹{amt} has stayed idle for {days}+ days, earning only {rate}% p.a.",
                "hi": f"लगभग ₹{amt} आपके खाते में {days}+ दिनों से पड़ा है, सिर्फ {rate}% सालाना ब्याज पर।",
            },
            "cta": {"en": "Open a Sweep FD", "hi": "स्वीप FD खोलें"},
        }
    if t == "contextual_spend":
        merch = str(e.get("merchant", "")).title()
        amt = _rupee(e.get("amount"))
        return {
            "title": {"en": f"Recent {e.get('spend_kind','')} purchase",
                      "hi": "हाल की खरीद पर सुरक्षा"},
            "body": {
                "en": f"You spent ₹{amt} on {merch}. Want optional {e.get('cover_type','cover')}?",
                "hi": f"आपने {merch} पर ₹{amt} खर्च किए। क्या इसके लिए वैकल्पिक कवर चाहिए?",
            },
            "cta": {"en": "Add optional cover", "hi": "वैकल्पिक कवर जोड़ें"},
        }
    # salary_jump
    prev = _rupee(e.get("previous_salary"))
    latest = _rupee(e.get("latest_salary"))
    return {
        "title": {"en": "Income just went up", "hi": "आपकी आय बढ़ी है"},
        "body": {
            "en": f"Your salary rose from ₹{prev} to ₹{latest}. A good time to add simple protection.",
            "hi": f"आपकी सैलरी ₹{prev} से बढ़कर ₹{latest} हो गई। साधारण सुरक्षा जोड़ने का अच्छा समय।",
        },
        "cta": {"en": "Add simple cover", "hi": "साधारण कवर जोड़ें"},
    }


def _order(moments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rank = {t: i for i, t in enumerate(PRIORITY)}
    return sorted(moments, key=lambda m: rank.get(m["trigger_type"], 99))


def run_agent_deterministic(
    persona: dict[str, Any],
    moments: list[dict[str, Any]],
    *,
    skipped_types: set[str] | None = None,
) -> dict[str, Any]:
    """Rule-based perceive→reason→act, calling the real tools and logging each step."""
    skipped_types = skipped_types or set()
    log: list[dict[str, Any]] = []
    pid = persona.get("persona_id", "?")
    log.append({"step": "perceive", "detail": f"{len(moments)} candidate moment(s) for {pid}: "
                                              + ", ".join(m["trigger_type"] for m in moments)})

    if not moments:
        log.append({"step": "act", "detail": "Nothing worth surfacing — staying silent."})
        return {"action": "stay_silent", "decision_log": log, "engine": "deterministic"}

    ordered = _order(moments)
    hero = ordered[0]
    suppressed = [
        {"trigger_type": m["trigger_type"],
         "reason": f"lower value than {hero['trigger_type']} this session"}
        for m in ordered[1:]
    ]
    for s in suppressed:
        log.append({"step": "suppress", "tool": None,
                    "detail": f"Suppressed {s['trigger_type']} — {s['reason']}."})

    # Reason: ground the chosen moment.
    product = _product_for(hero)
    rag_q = f"{product['type'].replace('_',' ')} {hero['trigger_type'].replace('_',' ')}"
    hits = rag.query_rag(rag_q, 3)
    log.append({"step": "reason", "tool": "query_rag",
                "detail": f"query: '{rag_q}'", "result": [h["id"] for h in hits]})

    # Reason: suitability (a recent skip of this category suppresses it — the
    # feedback loop teaching the agent to back off).
    fit = suitability.check_suitability(
        product_type=product["type"],
        monthly_cost=product["monthly_cost"],
        persona=persona,
        recently_skipped=hero["trigger_type"] in skipped_types,
    )
    log.append({"step": "reason", "tool": "check_suitability",
                "detail": f"{product['type']} @ ₹{product['monthly_cost']}/mo",
                "result": "suitable" if fit["suitable"] else "; ".join(fit["blocks"])})

    if not fit["suitable"]:
        log.append({"step": "act", "detail": "Suppressed — failed suitability. Not surfaced."})
        return {"action": "suppress", "reason": fit["blocks"], "suitability": fit,
                "suppressed": suppressed, "decision_log": log, "engine": "deterministic"}

    # Reason: build the honest comparison for the insurance flow.
    comparison_available = False
    if hero["trigger_type"] == "premium_leak":
        cmp = comparison.build_insurance_comparison(hero["evidence"].get("competitor"))
        comparison_available = cmp is not None
        log.append({"step": "reason", "tool": "build_comparison",
                    "detail": "term insurance, like-for-like",
                    "result": f"competitor wins: {', '.join(cmp['competitor_wins'])}" if cmp else "n/a"})

    nudge = _bilingual(hero)
    log.append({"step": "act",
                "detail": f"Surfacing {hero['trigger_type']} in EN/हिंदी with Skip + "
                          "human-advisor options."})

    return {
        "action": "surface",
        "surfaced_moment": hero,
        "product": {"type": product["type"], "doc_id": product["doc_id"],
                    "monthly_cost": product["monthly_cost"]},
        "suitability": fit,
        "comparison_available": comparison_available,
        "nudge": nudge,
        "suppressed": suppressed,
        "decision_log": log,
        "engine": "deterministic",
        "model": "rules (no ANTHROPIC_API_KEY set)",
    }


def run_agent(
    persona: dict[str, Any],
    moments: list[dict[str, Any]],
    *,
    skipped_types: set[str] | None = None,
) -> dict[str, Any]:
    """Entry point. Uses the LLM loop when a key is present, else deterministic."""
    if config.has_api_key():
        try:
            from engine.agent_llm import run_agent_llm

            return run_agent_llm(persona, moments, skipped_types=skipped_types)
        except Exception as exc:  # never break the demo on an LLM hiccup
            result = run_agent_deterministic(persona, moments, skipped_types=skipped_types)
            result["llm_error"] = f"{type(exc).__name__}: {exc}"
            return result
    return run_agent_deterministic(persona, moments, skipped_types=skipped_types)
