"""Agent core — the perceive → reason → act → learn loop.

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
    tools, with pre-authored EN/हिंदी copy.

Both paths share two helpers so they behave identically regardless of engine:
  * `apply_learning` — the close of the loop: drop already-adopted features and
    recently-skipped categories, emitting a visible LEARN step for each.
  * `materialize_flow` — assembles the flow-specific UI payload from grounded
    builders, so every flow renders the same whether rules or the LLM decided.
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
    "salary_jump",       # income grew → honest open-shelf investing (Flow C hero)
    "contextual_spend",
]


def _order(moments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rank = {t: i for i, t in enumerate(PRIORITY)}
    return sorted(moments, key=lambda m: rank.get(m["trigger_type"], 99))


def _rupee(n: Any) -> str:
    try:
        return f"{int(round(float(n))):,}"
    except (TypeError, ValueError):
        return str(n)


def _pretty(trigger_type: str) -> str:
    return trigger_type.replace("_", " ")


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
    if cat == "invest_shelf":
        return {"type": "investment", "monthly_cost": 0, "doc_id": "yono-investment-shelf"}
    return {"type": "unknown", "monthly_cost": 0, "doc_id": None}


# Categories where the recommendation is an investment/SBI-product surface — the
# UI shows a neutrality line ("you're seeing this because it fits, not because
# it's ours; YONO lists the whole market") to make the open-shelf posture real.
_NEUTRALITY_CATEGORIES = {"fixed_deposit", "insurance_compare", "subscription_review"}


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
        name, amt = str(f.get("name", "")).title(), _rupee(f.get("amount"))
        soon = e.get("renews_in_days", f.get("next_charge_in_days"))
        return {
            "title": {"en": "A subscription renews soon", "hi": "एक सदस्यता जल्द रिन्यू होगी"},
            "body": {"en": f"Heads up — {name} (₹{amt}/mo) renews in {soon} days. If you're not "
                           "using it, pause it and put that money toward your dream instead.",
                     "hi": f"ध्यान दें — {name} (₹{amt}/माह) {soon} दिनों में रिन्यू होगा। अगर आप इसका "
                           "इस्तेमाल नहीं कर रहे, तो इसे रोककर वह पैसा अपने सपने में लगाएँ।"},
            "cta": {"en": "Review & invest instead", "hi": "देखें और निवेश करें"},
        }
    # salary_jump → honest open-shelf investing
    prev, latest = _rupee(e.get("previous_salary")), _rupee(e.get("latest_salary"))
    return {
        "title": {"en": "Your income just grew", "hi": "आपकी आय बढ़ी है"},
        "body": {"en": f"Your salary rose from ₹{prev} to ₹{latest}. Want to put part of your raise "
                       "to work — across the whole market, not just SBI's funds?",
                 "hi": f"आपकी सैलरी ₹{prev} से बढ़कर ₹{latest} हो गई। क्या अपनी बढ़ोतरी का कुछ हिस्सा "
                       "निवेश करना चाहेंगे — सिर्फ़ SBI के नहीं, पूरे बाज़ार के फंड्स में?"},
        "cta": {"en": "See investment options", "hi": "निवेश विकल्प देखें"},
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


# --- Shared payload assembly (used by BOTH engines) -------------------------
def materialize_flow(
    persona: dict[str, Any], moment: dict[str, Any], adopted_features: set[str] | None = None
) -> dict[str, Any]:
    """Assemble the flow-specific UI payload for a surfaced moment.

    Pure assembly from the grounded builders (comparison / goal_engine /
    adoption_ladder) — shared by the deterministic and LLM paths so every flow
    renders identically regardless of which engine decided. Returns only the
    extra fields to merge onto the decision (no action / log / nudge)."""
    adopted_features = set(adopted_features or set())
    tt = moment["trigger_type"]
    e = moment.get("evidence", {})

    if moment.get("suggested_category") == "invest_shelf":
        from engine import investment_shelf
        return {
            "flow": "invest_shelf",
            "investment_shelf": investment_shelf.build_shelf(),
            # The open-shelf nudge carries the neutrality line too.
            "neutral_disclosure": True,
        }

    if tt == "feature_discovery":
        return {
            "flow": "feature_discovery",
            "walkthrough": {
                "feature": e.get("feature"),
                "display": e.get("display_name"),
                "steps": e.get("steps", []),
                "time_seconds": e.get("time_seconds"),
            },
            "ladder": adoption_ladder.state(adopted_features),
            "unlocks": e.get("unlocks"),
        }

    if tt == "subscription_saver":
        flagged = e.get("flagged", {})
        amount = flagged.get("amount", 0)
        goal = goal_engine.primary_goal(persona)
        redirect = goal_engine.frame_redirect(goal, amount) if goal else None
        invest = None
        assumptions = rag.get_doc("invest-instead-returns")
        if assumptions:
            invest = goal_engine.invest_instead(
                amount,
                float(assumptions.meta.get("rd_pct", 7.0)),
                float(assumptions.meta.get("sip_illustrative_pct", 12.0)),
            )
        return {
            "flow": "subscription",
            "subscriptions": e.get("subscriptions", []),
            "flagged": flagged,
            "is_mandate": e.get("is_mandate", False),
            "total_monthly": e.get("total_monthly"),
            "potential_savings": e.get("potential_savings"),
            "goal_redirect": redirect,
            "invest": invest,
        }

    # product flows (idle→FD, premium-leak→compare, salary/spend→micro-cover)
    product = _product_for(moment)
    fit = suitability.check_suitability(
        product_type=product["type"], monthly_cost=product["monthly_cost"], persona=persona
    )
    comparison_available = (
        tt == "premium_leak"
        and comparison.build_insurance_comparison(e.get("competitor")) is not None
    )
    return {
        "flow": "product",
        "product": product,
        "suitability": fit,
        "comparison_available": comparison_available,
        # The open-shelf neutrality line is shown for SBI-product surfaces.
        "neutral_disclosure": moment["suggested_category"] in _NEUTRALITY_CATEGORIES,
    }


# --- The learn close of the loop (shared by BOTH engines) -------------------
def apply_learning(
    persona: dict[str, Any],
    moments: list[dict[str, Any]],
    skipped_types: set[str],
    adopted_features: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Filter candidate moments using what Saarthi has already learned, emitting
    a visible LEARN step for each adaptation. Returns (kept_moments, learn_steps).

    * An already-adopted feature is dropped, and the ladder is ADVANCED — the
      agent synthesizes a grounded nudge for the next never-used rung (Bill Pay →
      AutoPay → Credit Score), so adoption compounds instead of repeating.
    * A recently-skipped category is suppressed — the agent backs off rather
      than nagging, and looks for the next-best moment.
    Run before either engine reasons, so the loop is identical regardless of
    which one is live (we never trust the LLM to honour this on its own)."""
    from engine import feature_blindspot

    learn: list[dict[str, Any]] = []
    kept: list[dict[str, Any]] = []
    advanced_to: set[str] = set()
    for m in moments:
        tt = m["trigger_type"]
        feat = m.get("evidence", {}).get("feature")
        if tt == "feature_discovery" and feat in adopted_features:
            disp = adoption_ladder.DISPLAY.get(feat, feat)
            # Advance to the next rung the user has NOT already adopted.
            nxt = adoption_ladder.next_after(feat)
            while nxt and nxt in adopted_features:
                nxt = adoption_ladder.next_after(nxt)
            if not nxt:
                learn.append({"step": "learn", "detail": f"You adopted {disp} — you've climbed the "
                                                         "whole adoption ladder."})
                continue
            learn.append({"step": "learn", "detail": f"You adopted {disp} — unlocking "
                                                      f"{adoption_ladder.DISPLAY.get(nxt, nxt)} next."})
            already = any(k.get("evidence", {}).get("feature") == nxt for k in kept)
            if (nxt not in advanced_to and not already
                    and "feature_discovery" not in skipped_types):
                syn = feature_blindspot.moment_for_feature(persona, nxt)
                if syn:
                    kept.append(syn)
                    advanced_to.add(nxt)
            continue
        if tt in skipped_types:
            learn.append({"step": "learn", "detail": f"You skipped {_pretty(tt)} before — backing off "
                                                     "and looking for your next-best moment instead."})
            continue
        kept.append(m)
    return kept, learn


def _learn_state(skipped_types: set[str], adopted_features: set[str]) -> dict[str, Any]:
    """A compact, persistent profile of what Saarthi has learned about a user."""
    adopted = [adoption_ladder.DISPLAY.get(f, f.replace("_", " ").title()) for f in sorted(adopted_features)]
    skipped = [_pretty(t) for t in sorted(skipped_types)]
    bits = []
    if adopted:
        bits.append(f"remembers this user adopted {', '.join(adopted)}")
    if skipped:
        bits.append(f"is backing off {', '.join(skipped)}")
    note = ("Saarthi " + " and ".join(bits) + ".") if bits \
        else "No feedback yet — Saarthi is still observing this user."
    return {"adopted": adopted, "skipped": skipped, "note": note}


# --- Per-flow decisions (deterministic path) --------------------------------
def _decide_feature_discovery(persona, hero, suppressed, log, adopted) -> dict[str, Any]:
    e = hero["evidence"]
    hits = rag.query_rag(f"YONO {e.get('display_name')} {e.get('external_payee')}", 3)
    log.append({"step": "reason", "tool": "query_rag",
                "detail": f"feature one-pager for {e.get('feature')}",
                "result": [h["id"] for h in hits]})
    log.append({"step": "reason", "tool": "adoption_ladder",
                "detail": "next unlock after first-time use",
                "result": f"{e.get('feature')} -> unlocks {e.get('unlocks')}"})
    log.append({"step": "act", "detail": "Surfacing a one-time discovery nudge + guided walkthrough "
                                         "in EN/हिंदी (discovery, not a sale)."})
    out = _base(hero, suppressed, log, _bilingual(hero))
    out.update(materialize_flow(persona, hero, adopted))
    return out


def _decide_subscription(persona, hero, suppressed, log) -> dict[str, Any]:
    hits = rag.query_rag("subscription autopay mandate pause category", 3)
    log.append({"step": "reason", "tool": "query_rag", "detail": "subscription map + AutoPay one-pager",
                "result": [h["id"] for h in hits]})
    payload = materialize_flow(persona, hero)
    redirect = payload.get("goal_redirect")
    if redirect:
        log.append({"step": "reason", "tool": "goal_engine",
                    "detail": f"redirect ₹{_rupee(payload['flagged'].get('amount'))} -> {redirect['label']}",
                    "result": f"{redirect['pct_before']}% -> {redirect['pct_after']}%"})
    invest = payload.get("invest")
    if invest:
        five = next((s for s in invest["scenarios"] if s["years"] == 5), invest["scenarios"][-1])
        log.append({"step": "reason", "tool": "project_investment",
                    "detail": f"₹{_rupee(invest['monthly'])}/mo invested (RD {invest['rd_pct']}% / SIP "
                              f"{invest['sip_pct']}% illustrative)",
                    "result": f"5y SIP ≈ ₹{_rupee(five['sip_value'])} (not guaranteed)"})
    log.append({"step": "act", "detail": "Surfacing a gentle pre-renewal reminder (no usage claim — "
                                         "we only see the mandate) + an honest invest-instead "
                                         "illustration. Cancellation is guided; mandates can be paused."})
    out = _base(hero, suppressed, log, _bilingual(hero))
    out.update(payload)
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
    if hero["trigger_type"] == "premium_leak":
        cmp = comparison.build_insurance_comparison(hero["evidence"].get("competitor"))
        log.append({"step": "reason", "tool": "build_comparison", "detail": "term insurance, like-for-like",
                    "result": f"competitor wins: {', '.join(cmp['competitor_wins'])}" if cmp else "n/a"})
    log.append({"step": "act", "detail": f"Surfacing {hero['trigger_type']} in EN/हिंदी with Skip + "
                                         "human-advisor options."})
    out = _base(hero, suppressed, log, _bilingual(hero))
    out.update(materialize_flow(persona, hero))
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
    pid = persona.get("persona_id", "?")

    log: list[dict[str, Any]] = []
    log.append({"step": "perceive", "detail": f"{len(moments)} candidate moment(s) for {pid}: "
                                              + (", ".join(m["trigger_type"] for m in moments) or "none")})
    # Close the loop first: apply what we've learned about this user.
    moments, learn = apply_learning(persona, moments, skipped_types, adopted_features)
    log.extend(learn)
    if not moments:
        log.append({"step": "act", "detail": "Nothing left worth surfacing — staying silent."})
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
    """Entry point. Uses the LLM loop when a key is present, else deterministic.
    Either way, attaches the learned-profile so the UI can show what Saarthi
    remembers about this user."""
    skipped_types = skipped_types or set()
    adopted_features = adopted_features or set()
    if config.has_api_key():
        try:
            from engine.agent_llm import run_agent_llm

            result = run_agent_llm(persona, moments, skipped_types=skipped_types,
                                   adopted_features=adopted_features)
        except Exception as exc:  # never break the demo on an LLM hiccup
            result = run_agent_deterministic(persona, moments, skipped_types=skipped_types,
                                             adopted_features=adopted_features)
            result["llm_error"] = f"{type(exc).__name__}: {exc}"
    else:
        result = run_agent_deterministic(persona, moments, skipped_types=skipped_types,
                                         adopted_features=adopted_features)
    result["learn_state"] = _learn_state(skipped_types, adopted_features)
    return result
