# Saarthi — Add-On Flows (Digital Adoption)
### Extension spec for Claude Code

> **Read `saarthi-context.md` (or `CLAUDE.md`) first.** This file is a *delta* on top of it. All
> conventions there still hold: FastAPI backend, Anthropic agent core (perceive→reason→act→learn),
> RAG over FAISS, rule-based suitability filter, SQLite feedback store, React mocked-YONO shell,
> **synthetic data only**, and **`ANTHROPIC_API_KEY` is the only required secret** (no new keys, no
> real banking/MCP connectors). This file adds new flows; it does not change the architecture.

---

## 0. What this adds (and why)

The existing prototype has product-adoption flows (idle→FD, insurance honest-comparison,
salary→micro-cover). Those prove "Saarthi recommends products." This add-on adds the flows that
prove **platform / Digital Adoption** — the actual problem statement — plus a high-demand
engagement bridge. New work:

1. **Flow D — Explorer → Feature Discovery** (HERO) — drives *platform* adoption.
2. **Subscription Saver** — high-demand feature + engagement→adoption bridge.
3. **Goal Engine** — folded into existing flows (NOT a standalone flow).
4. **Vernacular/voice** — demonstrated *inside* Flow D (Bharat proof).

---

## 1. Strategic rule (enforce this while building)

- **Platform adoption > product adoption** for this hackathon. The flow that wins is the one that
  moves a user *beyond UPI + balance-check* — not another product sale.
- **Do NOT proliferate flows.** Build exactly the canonical set in §2. Anything else
  (e.g. a "habit builder" / weekly-coaching flow) is **Digital Engagement**, a different pillar —
  leave it as a roadmap stub, do not build it into the demo.
- Each flow must map to a *distinct* adoption dimension. If a new flow duplicates a dimension
  already covered, fold it in instead of adding it.

---

## 2. Canonical flow set (the only flows in the demo)

| # | Flow | Adoption dimension | Status |
|---|------|--------------------|--------|
| 1 | Explorer → Feature Discovery (**Flow D**) | Platform adoption | **NEW — hero** |
| 2 | Insurance honest-comparison | Trust-first product adoption | built |
| 3 | Subscription Saver | Engagement → adoption bridge | **NEW** |
| 4 | Idle → Goal → Sweep-FD / SIP | Investment adoption (goal-driven) | built + **Goal Engine new** |
| — | Vernacular / voice | Bharat adoption (cross-cutting) | demoed inside Flow D |

---

## 3. FLOW D — Explorer → Feature Discovery  (HERO)

**One-liner for the agent's purpose:** Saarthi is an *agentic Digital Adoption Platform* — unlike
static tooltip tools that show the same guidance to everyone, it detects each user's feature blind
spot from their own transaction behaviour and guides only the one relevant, never-used feature.

### Persona
`Explorer` — uses YONO only for UPI + balance check. Never opened Bill Pay, Credit Score, Card
Controls, FD, or Investments.

### Trigger logic (build in the trigger engine)
A "feature blind spot" fires when BOTH hold:
```text
1. Narrow-usage signal:  user's YONO actions over last N days ⊆ {UPI, balance_check}
2. Relevance signal:     a specific unused feature is evidenced by behaviour
                         e.g. recurring electricity payment leaving to a NON-YONO payee
                         → "YONO Bill Pay" is relevant AND never used
```
Relevance sources to implement (pick the strongest for demo = bill pay):
- Recurring utility payment to an external payee → **Bill Pay**
- Repeated manual same-payee transfer → **AutoPay / mandate**
- Loan/EMI present but score never checked → **Credit Score**
- Card spends but no controls set → **Card Controls**

### Agent reasoning (agent core)
```text
User already pays this bill digitally (just not in YONO)
        ↓
YONO Bill Pay is relevant
        ↓
Feature has never been used by this user
        ↓
Worth a ONE-TIME discovery nudge (suppress if skipped recently)
```

### What the user sees (Saarthi card)
> You pay your electricity bill every month using another app.
> YONO can do this in under 30 seconds. Want me to show you?

Buttons: **Show me** · **Not interested**

### Guided experience (coachmark walkthrough overlay)
```text
Bill Payments → Electricity → Select provider → Complete payment (first time)
```

### Learn step (feedback store) — the "adoption ladder"
```text
Feature adopted (Bill Pay)
        ↓
Unlock adjacent suggestion: AutoPay  →  then Credit Score  →  then FD
```
Implement an **adoption ladder**: each adopted feature unlocks the next adjacent suggestion.
This demonstrates compounding platform depth, not a one-off nudge. Store ladder state per user.

### Why this is the easiest clean demo
It needs only a coachmark overlay on a mocked Bill-Pay screen + the trigger. Prioritise polishing
this flow's walkthrough — it is the visual centrepiece of the Digital-Adoption story.

---

## 4. Subscription Saver

### Persona
`Subscription Saver` — multiple recurring OTT / fitness / cloud-storage debits, some unused.

### Flow (build in this order)
```text
Subscription detection
        ↓
Category grouping (OTT / fitness / storage)
        ↓
Usage analysis (last 30 days per app, from synthetic usage signal)
        ↓
Unused alert + renewal warning (3 days before charge)
        ↓
One-click review
        ↓
Cancellation assist (GUIDED — see guardrail)
        ↓
Savings redirect ("Move ₹450 to your bike goal?")  ← hands off to Goal Engine
        ↓
Confirmation + habit loop trigger
```

### Detection logic
Cluster recurring debits by (payee, cadence ≈ monthly, amount stability). Tag category from a
small payee→category map in the RAG corpus. Flag "unused" via the synthetic per-app usage signal.

### TWO REQUIRED FIXES (do not skip)
1. **No auto-cancellation of third-party apps.** Deep-linking into Netflix/Hotstar to cancel is
   messy and undemoable. Implement cancellation as: **renewal warning → guided steps + set a
   reminder → redirect the saved amount to a goal.** Never claim Saarthi cancelled a third-party
   subscription on its own.
2. **Lead with the SBI-native advantage.** Many Indian subscriptions run on **UPI AutoPay /
   e-mandates**, which the bank sees *at source* — unlike third-party trackers that screen-scrape.
   Surface this in copy: "SBI sees the mandate directly." Where the subscription is a UPI mandate,
   offer in-app **pause/stop the mandate** (mock it) — this is a genuine, ownable capability.

### Adoption value (why it belongs in a Digital-Adoption demo)
It's the most-wanted in-app banking capability in global benchmarks, and the savings-redirect step
is the bridge that pulls users into goals → FD/SIP. It connects engagement to adoption.

---

## 5. Goal Engine (fold-in — NOT a standalone flow)

Do not build a separate "goal-based agent" flow. Instead build a **goal engine** that several
flows feed into, so nudges feel like advice toward the user's own goal rather than a product push.

- **Data:** a user can hold goals: `{goal_id, label, target_amount, target_date, saved_so_far}`
  (e.g. "₹2 lakh in 18 months", "Buy a bike").
- **Inputs feed it:** Subscription Saver redirect, idle-balance sweep, salary inflow.
- **Output:** the engine turns a generic nudge into a goal-framed one
  ("Move ₹450 to your bike goal — you'd be 32% there") and recommends the vehicle (RD/SIP/FD)
  via the existing suitability filter.
- **Reuse, don't duplicate:** route all product recommendations through the existing
  suitability filter + RAG honest-math. The Goal Engine only adds the *framing and target math*.

---

## 6. Vernacular / voice (cross-cutting — demo inside Flow D)

Not a separate flow. Demonstrate the existing EN/हिंदी toggle + voice on the **Flow D** card:
- Rural `Explorer` persona hears the discovery nudge in Hindi (Web Speech TTS) and can respond by
  voice ("हाँ, दिखाओ").
- Use it to tell the Bharat story: voice-guided feature discovery is how users beyond metros move
  past UPI-only usage. This is SBI's structural advantage — make it visible, don't add a flow.

---

## 7. New backend components

Add to the FastAPI service (extend, don't rewrite):

```text
trigger_engine/
  feature_blindspot.py     # narrow-usage ∩ relevance → Flow D event
  subscription_detector.py # recurring-charge clustering + unused/renewal flags

agent/
  adoption_ladder.py       # per-user unlock state (feature → next feature)
  goal_engine.py           # goal math + goal-framed nudge assembly

# reuse as-is: agent core loop, RAG, suitability filter, XAI builder, feedback store
```
Every new trigger still flows through the **same agent loop** (perceive→reason→act→learn) and logs
its decision — keep the "autonomous agent decides whether to act / can suppress" behaviour.

---

## 8. New synthetic data / personas

Extend the generator with these personas and signals (still 100% synthetic, no PII):

**Explorer**
```json
{ "persona": "explorer",
  "yono_actions_30d": ["upi","balance_check","upi","upi","balance_check"],
  "external_recurring": [{ "payee":"BESCOM ELECTRICITY", "via":"PhonePe", "amount":1180, "cadence":"monthly" }],
  "features_ever_used": ["upi","balance_check"] }
```

**Subscription Saver** — add subscription/mandate records:
```json
{ "subscriptions": [
    { "sub_id":"s1", "name":"NETFLIX",  "category":"OTT",     "amount":649, "cadence":"monthly",
      "via":"UPI_AUTOPAY", "used_last_30d": true,  "next_charge_in_days": 3 },
    { "sub_id":"s2", "name":"CULT FIT",  "category":"FITNESS", "amount":1300,"cadence":"monthly",
      "via":"UPI_AUTOPAY", "used_last_30d": false, "next_charge_in_days": 9 },
    { "sub_id":"s3", "name":"GOOGLE ONE","category":"STORAGE", "amount":130, "cadence":"monthly",
      "via":"card",        "used_last_30d": false, "next_charge_in_days": 14 }
] }
```

**Goals** (attach to any persona):
```json
{ "goals": [ { "goal_id":"g1", "label":"Buy a bike", "target_amount":120000, "target_date":"2027-06-01", "saved_so_far":38000 } ] }
```

**RAG corpus additions:** a payee→category map (for subscription/bill classification) and short
YONO feature one-pagers (Bill Pay, AutoPay, Credit Score, Card Controls) so the discovery copy and
walkthrough steps are grounded, not invented.

---

## 9. New frontend components (React, mocked-YONO shell)

- **Feature-discovery coachmark walkthrough** — overlay highlighting real buttons on a mocked
  Bill-Pay screen (Bill Payments → Electricity → Provider → Pay). This is the hero visual.
- **Subscription dashboard card** — grouped list (OTT/fitness/storage), unused tag, renewal
  countdown, "review" + "redirect savings" actions; for UPI-mandate items show "pause mandate".
- **Goal redirect card** — "Move ₹X to [goal] — you'd be Y% there", with progress bar.
- Reuse existing: Saarthi nudge card, EN/हिंदी toggle, voice, "Why am I seeing this?" XAI card,
  consent gate.

---

## 10. Guardrails (additions to the parent file's list)

- Flow D nudges are **discovery, not sales** — surface a feature the user already needs; never
  upsell a paid product inside the discovery card.
- Subscription cancellation is **guided only** — never auto-cancel a third-party service; for UPI
  mandates, pausing/stopping is allowed (and is the SBI-native advantage) but **mock** it.
- One discovery nudge at a time; respect "Not interested" (suppress that feature for the session).
- Do **not** build the habit-builder/weekly-coaching flow into the demo (it's Digital Engagement).

---

## 11. Build order for the add-ons

1. Extend synthetic data: Explorer, Subscription Saver, Goals, RAG payee/feature docs.
2. `feature_blindspot.py` trigger + Flow D agent reasoning → fire the bill-pay discovery event.
3. Flow D frontend: discovery card + **coachmark walkthrough** (the hero — polish this most).
4. `adoption_ladder.py` — unlock next feature after first-time use; show it in the demo.
5. `subscription_detector.py` + subscription dashboard card + renewal warning.
6. `goal_engine.py` + goal redirect card; wire Subscription Saver's redirect into it.
7. Vernacular/voice pass on the Flow D card.
8. Log every agent decision; verify the loop visibly "decides whether to act."

---

## 12. Demo additions & grounded talking points

Add to the demo script (these stats are for the pitch/voiceover — do not hardcode them in app
logic):
- Industry-average core-feature adoption is only ~24.5% — most features are never used. Flow D
  attacks exactly this.
- Bill pay leaks to third parties: PhonePe + Google Pay control 83%+ of UPI volume, and BBPS/
  Paytm/PhonePe dominate utility bill payments — yet YONO has the same biller built in.
- Subscription management is the ~2nd most-wanted mobile-banking feature (≈32% rate it
  "extremely valuable"; ~$200/yr/ user wasted on unused subs) — Saarthi ships it.

**Key presentation line for Flow D:**
> "The first flows drive product adoption. Flow D drives *platform* adoption — Saarthi finds the
> capabilities a customer would genuinely benefit from and guides them through first-time use,
> moving users beyond UPI and balance checks. Static tools show everyone the same tooltip; Saarthi
> is an agent that knows *your* blind spot."

---

## 13. Secrets / dependencies

No new secrets. No new MCP connectors. Everything runs on the parent file's stack with
`ANTHROPIC_API_KEY` only. Synthetic data only — never connect real customer or banking data.

*End of add-on. Build the canonical set (§2), make Flow D the hero, keep the agent loop visibly
autonomous, and resist adding flows beyond §2.*
