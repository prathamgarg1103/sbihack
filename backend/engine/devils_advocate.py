"""Devil's advocate — a second reasoning pass that argues AGAINST every nudge.

Before anything is surfaced, this pass asks: "why should this user NOT do
this?" A strong objection suppresses the nudge (and the reason is logged); a
weak objection is attached to the explainability payload so the user sees both
sides on the "Why am I seeing this?" card.

This module is the deterministic rule path (canned objections keyed by trigger
type: lock-in risk, emergency-fund depletion, cover overlap, attention cost).
`agent_llm` runs a real second LLM pass and falls back to these rules whenever
the model's answer can't be parsed.
"""
from __future__ import annotations

from typing import Any

# score >= threshold -> the objection is strong -> suppress the nudge.
STRONG_THRESHOLD = 0.7


def _verdict(score: float) -> tuple[str, str]:
    strong = score >= STRONG_THRESHOLD
    return ("strong" if strong else "weak", "suppress" if strong else "attach")


def challenge(moment: dict[str, Any], persona: dict[str, Any]) -> dict[str, Any]:
    """Argue against the moment. Returns objection (EN/हिंदी), strength, verdict."""
    tt = moment.get("trigger_type", "")
    e = moment.get("evidence", {}) or {}
    income = float(persona.get("monthly_income", 0) or 0)

    score = 0.35
    if tt == "idle_balance":
        idle = float(e.get("idle_amount", 0) or 0)
        buffer_floor = max(25_000.0, 0.5 * income)
        if idle and idle < buffer_floor:
            score = 0.9
            en = (f"₹{idle:,.0f} may be this user's entire emergency buffer — locking it "
                  "away could hurt far more than 2.70% interest does. Do not surface.")
            hi = (f"₹{idle:,.0f} शायद इस उपयोगकर्ता का पूरा आपातकालीन फंड है — इसे लॉक करना "
                  "2.70% ब्याज से कहीं ज़्यादा नुकसानदेह हो सकता है।")
        else:
            en = ("This could be an emergency buffer. Mitigation: a Sweep-FD stays "
                  "withdrawable (only a 0.50% breakage penalty), so the lock-in risk is low.")
            hi = ("यह आपातकालीन फंड हो सकता है। लेकिन स्वीप-FD से पैसा कभी भी निकाला जा "
                  "सकता है (सिर्फ 0.50% पेनल्टी), इसलिए जोखिम कम है।")
    elif tt == "premium_leak":
        en = ("Switching insurers means a fresh proposal, fresh medical disclosures and a "
              "new 12-month suicide-exclusion clock — the annual saving is not free.")
        hi = ("बीमा कंपनी बदलने का मतलब है नया प्रस्ताव, नई स्वास्थ्य घोषणाएँ और 12 महीने की "
              "नई एक्सक्लूज़न अवधि — सालाना बचत मुफ़्त नहीं मिलती।")
    elif tt == "salary_jump":
        en = ("A raise is often already spoken for (rent, EMIs, family support), and a "
              "market-linked SIP can lose money — no need to rush the surplus.")
        hi = ("बढ़ी हुई सैलरी अक्सर पहले से खर्चों में बंधी होती है, और बाज़ार-आधारित SIP में "
              "नुकसान भी हो सकता है — जल्दबाज़ी की ज़रूरत नहीं।")
    elif tt == "contextual_spend":
        amount = float(e.get("amount", 0) or 0)
        if amount and amount < 8_000:
            score = 0.85
            en = (f"Cover on a ₹{amount:,.0f} purchase rarely pays for itself — the claim "
                  "hassle likely outweighs the benefit. Do not surface.")
            hi = (f"₹{amount:,.0f} की खरीद पर कवर शायद ही फ़ायदेमंद हो — क्लेम की झंझट लाभ "
                  "से ज़्यादा है।")
        else:
            en = ("The card used for this purchase may already bundle similar protection — "
                  "buying cover twice insures nothing extra.")
            hi = ("इस खरीद वाले कार्ड में शायद पहले से ऐसा कवर शामिल हो — दोबारा कवर लेने से "
                  "कुछ अतिरिक्त सुरक्षा नहीं मिलती।")
    elif tt == "feature_discovery":
        en = ("The user opened the app to finish a task — an interruption they didn't ask "
              "for has a real attention cost, even for a genuinely useful feature.")
        hi = ("उपयोगकर्ता अपना काम करने आया था — बिना माँगी रुकावट की एक कीमत होती है, भले "
              "ही फीचर उपयोगी हो।")
    elif tt == "subscription_saver":
        en = ("The bank cannot see whether they actually use this service — pausing the "
              "mandate could cancel something they love.")
        hi = ("बैंक यह नहीं देख सकता कि सेवा असल में इस्तेमाल हो रही है या नहीं — मैंडेट "
              "रोकने से कोई पसंदीदा सेवा बंद हो सकती है।")
    elif tt == "missold_product":
        en = ("Exiting now costs a surrender charge and the money stays locked till year 5. "
              "If the premium were comfortably affordable, staying could recoup the "
              "front-loaded charges — but here it clearly is not.")
        hi = ("अभी बाहर निकलने पर सरेंडर चार्ज लगेगा और पैसा 5वें साल तक लॉक रहेगा। अगर "
              "प्रीमियम आराम से चुकाया जा सकता, तो बने रहना बेहतर हो सकता था — पर यहाँ ऐसा "
              "नहीं है।")
    else:
        en = "No specific objection found — but every interruption has an attention cost."
        hi = "कोई विशेष आपत्ति नहीं — पर हर रुकावट की एक कीमत होती है।"

    strength, verdict = _verdict(score)
    return {
        "objection": {"en": en, "hi": hi},
        "strength": strength,
        "score": round(score, 2),
        "verdict": verdict,
        "engine": "rules",
    }
