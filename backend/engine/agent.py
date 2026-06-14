"""Agent core — the perceive → reason → act loop.

Given a persona's detected moments, the agent decides WHETHER to interrupt,
which product/feature fits, whether it passes suitability, and what the
(bilingual) nudge should say — logging every step so the autonomy is visible.

Flows handled:
  * product flows  — idle→FD, premium-leak→honest compare, salary/spend→cover
  * feature_discovery (Flow D, hero) — guide a never-used YONO feature + ladder
  * subscription_saver — review recurring charges, redirect savings to a goal

Two execution paths, same observable contract:
  * LLM path (ANTHROPIC_API_KEY set): a real Anthropic tool-calling loop.
  * Deterministic path (no key): rule-based orchestration calling the SAME
    tools, with pre-authored EN/हिंदी copy. This is what runs in the demo.
"""
from __future__ import annotations

from typing import Any

import config
from engine import adoption_ladder, comparison, goal_engine, rag, suitability

# Highest-value first — the agent surfaces one and suppresses the rest.
# Platform adoption (feature discovery) outranks product sales for this demo.
PRIORITY = [
    "feature_discovery",
    "premium_leak",
    "subscription_saver",
    "idle_balance",
    "contextual_spend",
    "salary_jump",
]


def _order(moments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rank = {t: i for i, t in enumerate(PRIORITY)}
    return sorted(moments, key=lambda m: rank.get(m["trigger_type"], 99))


def _rupee(n: Any) -> str:
    try:
        return f"{int(round(float(n))):,}"
    except (TypeError, ValueError):
        return str(n)


# --- Product mapping (for the product flows only) ---------------------------
def _product_for(moment: dict[str, Any]) -> dict[str, Any]:
    cat = moment["suggested_category"]
    ev = moment.get("evidence", {})
    if cat == "fixed_deposit":
        return {"type": "fixed_deposit", "monthly_cost": 0, "doc_id": "sbi-fd-sweep"}
    if cat == "insurance_compare":
        doc = rag.get_doc("sbi-life-eshield")
        cost = doc.meta.get("monthly_premium", 0) if doc else 0
        return {"type": "term_insurance", "monthly_cost": cost, "doc_id": "sbi-life-eshield"}
    if cat == "micro_cover":
        if str(ev.get("spend_kind", "")) == "electronics":
            return {"type": "device_insurance", "monthly_cost": 0, "doc_id": "sbi-general-device"}
        return {"type": "travel_insurance", "monthly_cost": 0, "doc_id": "sbi-general-travel"}
    return {"type": "unknown", "monthly_cost": 0, "doc_id": None}


# --- Bilingual copy ---------------------------------------------------------
def _bilingual(moment: dict[str, Any]) -> dict[str, dict[str, str]]:
    t = moment["trigger_type"]
    e = moment.get("evidence", {})
    if t == "premium_leak":
        comp, m, y = e.get("competitor"), _rupee(e.get("monthly_premium")), _rupee(e.get("annual_premium"))
        return {
            "title": {"en": "Recurring premium to another insurer",
                      "hi": "किसी और बीमा कंपनी को हर महीने प्रीमियम"},
            "body": {"en": f"You pay about ₹{m}/month (₹{y}/year) to {comp}. "
                           "Want an honest side-by-side comparison?",
                     "hi": f"आप हर महीने लगभग ₹{m} (₹{y}/साल) {comp} को देते हैं। "
                           "क्या आप एक ईमानदार तुलना देखना चाहेंगे?"},
            "cta": {"en": "See the honest comparison", "hi": "ईमानदार तुलना देखें"},
        }
    if t == "idle_balance":
        amt, days, rate = _rupee(e.get("idle_amount")), e.get("days_idle"), e.get("savings_rate_pct")
        return {
            "title": {"en": "Idle savings detected", "hi": "बचत खाते में पैसा बिना इस्तेमाल पड़ा है"},
            "body": {"en": f"About ₹{amt} has stayed idle for {days}+ days, earning only {rate}% p.a.",
                     "hi": f"लगभग ₹{amt} आपके खाते में {days}+ दिनों से पड़ा है, सिर्फ {rate}% सालाना ब्याज पर।"},
            "cta": {"en": "Open a Sweep FD", "hi": "स्वीप FD खोलें"},
        }
    if t == "contextual_spend":
        merch, amt = str(e.get("merchant", "")).title(), _rupee(e.get("amount"))
        return {
            "title": {"en": f"Recent {e.get('spend_kind','')} purchase", "hi": "हाल की खरीद पर सुरक्षा"},
            "body": {"en": f"You spent ₹{amt} on {merch}. Want optional {e.get('cover_type','cover')}?",
                     "hi": f"आपने {merch} पर ₹{amt} खर्च किए। क्या इसके लिए वैकल्पिक कवर चाहिए?"},
            "cta": {"en": "Add optional cover", "hi": "वैकल्पिक कवर जोड़ें"},
        }
    if t == "feature_discovery":
        disp, payee = e.get("display_name", "this feature"), str(e.get("external_payee", "this bill")).title()
        via, secs = e.get("via", "another app"), e.get("time_seconds", 30)
        return {
            "title": {"en": f"Try {disp} in YONO", "hi": f"YONO में {disp} आज़माएँ"},
            "body": {"en": f"You pay {payee} every month using {via}. YONO can do this in under "
                           f"{secs} seconds. Want me to show you?",
                     "hi": f"आप हर महीने {payee} का बिल {via} से भरते हैं। YONO में यह {secs} सेकंड "
                           "में हो जाता है। क्या मैं दिखाऊँ?"},
            "cta": {"en": "Show me", "hi": "मुझे दिखाओ"},
        }
    if t == "subscription_saver":
        f = e.get("flagged", {})
        name, amt, soon = str(f.get("name", "")).title(), _rupee(f.get("amount")), f.get("next_charge_in_days")
        n = len(e.get("subscriptions", []))
        return {
            "title": {"en": "Review your subscriptions", "hi": "अपनी सदस्यताएँ देखें"},
            "body": {"en": f"{name} (₹{amt}/mo) renews in {soon} days and you haven't used it in "
                           f"30 days. Review your {n} subscriptions?",
                     "hi": f"{name} (₹{amt}/माह) {soon} दिनों में रिन्यू होगा और आपने इसे 30 दिनों में "
                           f"इस्तेमाल नहीं किया। अपनी {n} सदस्यताएँ देखें?"},
            "cta": {"en": "Review subscriptions", "hi": "समीक्षा करें"},
        }
    # salary_jump
    prev, latest = _rupee(e.get("previous_salary")), _rupee(e.get("latest_salary"))
    return {
        "title": {"en": "Income just went up", "hi": "आपकी आय बढ़ी है"},
        "body": {"en": f"Your salary rose from ₹{prev} to ₹{latest}. A good time to add simple protection.",
                 "hi": f"आपकी सैलरी ₹{prev} से बढ़कर ₹{latest} हो गई। साधारण सुरक्षा जोड़ने का अच्छा समय।"},
        "cta": {"en": "Add simple cover", "hi": "साधारण कवर जोड़ें"},
    }


def _base(hero, suppressed, log, nudge) -> dict[str, Any]:
    return {
        "action": "surface",
        "surfaced_moment": hero,
        "nudge": nudge,
        "suppressed": suppressed,
        "decision_log": log,
        "engine": "deterministic",
        "model": "rules (no ANTHROPIC_API_KEY set)",
    }


# --- Per-flow decisions -----------------------------------------------------
def _decide_feature_discovery(persona, hero, suppressed, log, adopted) -> dict[str, Any]:
    e = hero["evidence"]
    hits = rag.query_rag(f"YONO {e.get('display_name')} {e.get('external_payee')}", 3)
    log.append({"step": "reason", "tool": "query_rag",
                "detail": f"feature one-pager for {e.get('feature')}",
                "result": [h["id"] for h in hits]})
    ladder = adoption_ladder.state(set(adopted) | set())
    log.append({"step": "reason", "tool": "adoption_ladder",
                "detail": "next unlock after first-time use",
                "result": f"{e.get('feature')} -> unlocks {e.get('unlocks')}"})
    log.append({"step": "act", "detail": "Surfacing a one-time discovery nudge + guided walkthrough "
                                         "in EN/हिंदी (discovery, not a sale)."})
    out = _base(hero, suppressed, log, _bilingual(hero))
    out["flow"] = "feature_discovery"
    out["walkthrough"] = {
        "feature": e.get("feature"),
        "display": e.get("display_name"),
        "steps": e.get("steps", []),
        "time_seconds": e.get("time_seconds"),
    }
    out["ladder"] = ladder
    out["unlocks"] = e.get("unlocks")
    return out


def _decide_subscription(persona, hero, suppressed, log) -> dict[str, Any]:
    e = hero["evidence"]
    hits = rag.query_rag("subscription autopay mandate pause category", 3)
    log.append({"step": "reason", "tool": "query_rag", "detail": "subscription map + AutoPay one-pager",
                "result": [h["id"] for h in hits]})
    flagged = e.get("flagged", {})
    goal = goal_engine.primary_goal(persona)
    redirect = goal_engine.frame_redirect(goal, flagged.get("amount", 0)) if goal else None
    if redirect:
        log.append({"step": "reason", "tool": "goal_engine",
                    "detail": f"redirect ₹{_rupee(flagged.get('amount'))} -> {redirect['label']}",
                    "result": f"{redirect['pct_before']}% -> {redirect['pct_after']}%"})
    log.append({"step": "act", "detail": "Surfacing subscription review. Cancellation is guided only; "
                                         "for UPI mandates, pause/stop is offered in-app."})
    out = _base(hero, suppressed, log, _bilingual(hero))
    out["flow"] = "subscription"
    out["subscriptions"] = e.get("subscriptions", [])
    out["flagged"] = flagged
    out["is_mandate"] = e.get("is_mandate", False)
    out["total_monthly"] = e.get("total_monthly")
    out["potential_savings"] = e.get("potential_savings")
    out["goal_redirect"] = redirect
    return out


def _decide_product(persona, hero, suppressed, log) -> dict[str, Any]:
    product = _product_for(hero)
    rag_q = f"{product['type'].replace('_',' ')} {hero['trigger_type'].replace('_',' ')}"
    hits = rag.query_rag(rag_q, 3)
    log.append({"step": "reason", "tool": "query_rag", "detail": f"query: '{rag_q}'",
                "result": [h["id"] for h in hits]})
    fit = suitability.check_suitability(product_type=product["type"],
                                        monthly_cost=product["monthly_cost"], persona=persona)
    log.append({"step": "reason", "tool": "check_suitability",
                "detail": f"{product['type']} @ ₹{product['monthly_cost']}/mo",
                "result": "suitable" if fit["suitable"] else "; ".join(fit["blocks"])})
    if not fit["suitable"]:
        log.append({"step": "act", "detail": "Suppressed — failed suitability. Not surfaced."})
        return {"action": "suppress", "reason": fit["blocks"], "suitability": fit,
                "suppressed": suppressed, "decision_log": log, "engine": "deterministic"}
    comparison_available = False
    if hero["trigger_type"] == "premium_leak":
        cmp = comparison.build_insurance_comparison(hero["evidence"].get("competitor"))
        comparison_available = cmp is not None
        log.append({"step": "reason", "tool": "build_comparison", "detail": "term insurance, like-for-like",
                    "result": f"competitor wins: {', '.join(cmp['competitor_wins'])}" if cmp else "n/a"})
    log.append({"step": "act", "detail": f"Surfacing {hero['trigger_type']} in EN/हिंदी with Skip + "
                                         "human-advisor options."})
    out = _base(hero, suppressed, log, _bilingual(hero))
    out["flow"] = "product"
    out["product"] = product
    out["suitability"] = fit
    out["comparison_available"] = comparison_available
    return out


def run_agent_deterministic(
    persona: dict[str, Any],
    moments: list[dict[str, Any]],
    *,
    skipped_types: set[str] | None = None,
    adopted_features: set[str] | None = None,
) -> dict[str, Any]:
    skipped_types = skipped_types or set()
    adopted_features = adopted_features or set()
    # Drop feature-discovery moments for features the user has already adopted —
    # the agent moves on rather than re-pitching a feature now in use.
    moments = [
        m for m in moments
        if not (m["trigger_type"] == "feature_discovery"
                and m.get("evidence", {}).get("feature") in adopted_features)
    ]
    log: list[dict[str, Any]] = []
    pid = persona.get("persona_id", "?")
    log.append({"step": "perceive", "detail": f"{len(moments)} candidate moment(s) for {pid}: "
                                              + ", ".join(m["trigger_type"] for m in moments)})
    if not moments:
        log.append({"step": "act", "detail": "Nothing worth surfacing — staying silent."})
        return {"action": "stay_silent", "decision_log": log, "engine": "deterministic"}

    ordered = _order(moments)
    hero = ordered[0]
    suppressed = [{"trigger_type": m["trigger_type"],
                   "reason": f"lower value than {hero['trigger_type']} this session"}
                  for m in ordered[1:]]
    for s in suppressed:
        log.append({"step": "suppress", "tool": None,
                    "detail": f"Suppressed {s['trigger_type']} — {s['reason']}."})

    tt = hero["trigger_type"]
    if tt in skipped_types:
        log.append({"step": "act", "detail": f"Suppressed {tt} — user skipped it recently. Backing off."})
        return {"action": "suppress", "reason": ["recently skipped"], "suppressed": suppressed,
                "decision_log": log, "engine": "deterministic"}

    if tt == "feature_discovery":
        return _decide_feature_discovery(persona, hero, suppressed, log, adopted_features)
    if tt == "subscription_saver":
        return _decide_subscription(persona, hero, suppressed, log)
    return _decide_product(persona, hero, suppressed, log)


def run_agent(
    persona: dict[str, Any],
    moments: list[dict[str, Any]],
    *,
    skipped_types: set[str] | None = None,
    adopted_features: set[str] | None = None,
) -> dict[str, Any]:
    """Entry point. Uses the LLM loop when a key is present, else deterministic."""
    if config.has_api_key():
        try:
            from engine.agent_llm import run_agent_llm

            return run_agent_llm(persona, moments, skipped_types=skipped_types)
        except Exception as exc:  # never break the demo on an LLM hiccup
            result = run_agent_deterministic(persona, moments, skipped_types=skipped_types,
                                             adopted_features=adopted_features)
            result["llm_error"] = f"{type(exc).__name__}: {exc}"
            return result
    return run_agent_deterministic(persona, moments, skipped_types=skipped_types,
                                   adopted_features=adopted_features)
