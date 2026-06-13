# Saarthi — Agentic Adoption Copilot for YONO
### Project context for Claude Code

> **How to use this file:** This is the single source of truth for the build. Drop it at the
> root of the repo. You can rename it to `CLAUDE.md` so Claude Code auto-loads it as context.
> It is scoped **only** to the SBI "Digital Adoption" problem statement — ignore the other two
> hackathon tracks. Build the prototype described in the **Prototype Scope** section; everything
> above it is the *why*, everything below it is the *how*.

---

## 0. TL;DR for the agent

We are building **Saarthi**, an **agentic AI adoption copilot** that lives inside a banking
super-app (modelled on SBI's YONO). It watches a user's own transaction patterns, detects
high-value "adoption moments," and surfaces **just-in-time, vernacular, trust-first nudges** that
co-pilot the user through an in-app journey they would otherwise never discover or trust.

The differentiator vs. every other team: **it is transparency-first, not sales-first.** Every
recommendation ships with an explainability card (the trigger, the honest math incl. charges,
what's *not* covered) and a hard suitability filter. This directly counters the documented
mis-selling that has poisoned trust in bank-sold insurance/investments.

**Only one secret is strictly required to run this: `ANTHROPIC_API_KEY`.** Everything else
(vector store, embeddings, TTS, data) can run locally and free. See Section 8.

---

## 1. Hackathon context (do not lose sight of these)

- **Event:** SBI Hackathon @ Global Fintech Fest (GFF) 2026 — "AI & Emerging Tech" track.
- **Hard requirement:** judges explicitly want **Agentic AI** ("autonomous agents that assist
  the bank"). The word "agent" / autonomous perceive→reason→act loop must be visible in the
  architecture, not bolted on.
- **Judging criteria (build to hit all four):**
  1. **Innovation** — originality (the mis-selling reframe is our edge).
  2. **Technical Feasibility** — must be a *working* prototype, not slideware.
  3. **Business Potential** — tie to SBI's real revenue (YONO earns ~₹100 cr/quarter in fee
     income from selling subsidiary insurance/MF products; we lift that *and* de-risk it).
  4. **Scalability** — framework reusable across YONO's 100+ planned "journeys."
- **Target app:** YONO 2.0 (~85M registered users; SBI wants it to eventually onboard 50% of
  its ~500M customer base; now multilingual; adding 100+ new journeys = "YONOnisation").

---

## 2. The problem statement (verbatim)

> **Digital Adoption** — Build contextual and adaptive AI experiences that encourage adoption of
> digital banking services including payments, investments, insurance, and mobile banking.

**Why we picked it:** it is the lowest-participation track (least flashy, hardest to demo a wow
moment), yet the highest-ROI lever for a bank — activating a dormant digital user costs a
fraction of acquiring a new one. Low competition + high business relevance.

---

## 3. The grounded problem (voice-of-customer research)

Real, sourced user pain with YONO, clustered. **Two buckets — respect the split when building
and pitching.** See Section 13 for sources.

### IN SCOPE — adoption barriers Saarthi solves
1. **UX complexity / discoverability.** YONO is widely rated as having poor UX: it crams in
   non-banking services, logs users off mid-task, the interface is "too sophisticated" for
   ordinary users, core journeys (e.g. add-beneficiary) crash mid-flow and force restarts, and
   MPIN/OTP buttons sometimes render off-screen. Users touch only UPI + balance-check and never
   discover deeper features.
2. **Investment adoption gap.** YONO has full mutual-fund investing, but users default to Groww
   because Groww's entire USP is simplicity ("give you *less*" — neat 3-section UI). SBI products
   (even the ₹250 JanNivesh SIP) ship simultaneously on Groww/Paytm/Zerodha, so YONO has no
   exclusivity moat — it competes on experience and loses.
3. **Insurance mis-selling — THE TRUST WOUND (our headline).** The human bancassurance channel
   is poisoned: documented cases of SBI staff forcing insurance as a condition for account
   opening, unauthorised deductions from savings accounts, coercing a home-loan customer into a
   ₹6 lakh policy to open a locker, pensioners duped into SBI Life policies. Banks receive the
   most mis-selling complaints of any channel (12,000+ in a single year). SBI has issued internal
   directives to curb it — they are *already under pressure to fix this*.
4. **The Bharat gap.** A large share of SBI's rural/semi-urban base can't or won't use YONO due
   to smartphone access, language, and awareness. ~35% of Indian women own smartphones; rural UPI
   preference ~38%. Vernacular + voice is the only way to reach this half of the base.

### CONTEXT ONLY — do NOT claim Saarthi fixes these (reference as *cause* of dormancy)
5. **Reliability collapse.** Chronic "Something went wrong" errors; #sbidown trends during
   outages; UPI fails mid-transaction; salaries stuck. This *causes* the distrust that drives
   dormancy — but we do not fix servers.
6. **Onboarding/auth friction.** Dual-SIM/eSIM registration breaks; SMS verification fails; OTP
   fatigue (re-asks every action). Infra-level, not our agent's job.

### The reframe that wins the room
Insurance/investment adoption isn't broken from lack of demand (91% of Indian account-holders are
open to transaction-based offers). It's broken because the **channel** is a coercive, opaque,
target-driven human machine customers have learned to fear. **Saarthi moves that sale from a
coercive human channel to a transparent, opt-in, suitability-filtered, explainable digital one.**
We are not pitching "cross-sell." We are pitching **mis-selling remediation disguised as an
adoption engine** — something SBI is already scrambling to deliver.

---

## 4. The solution — Saarthi

An agentic layer inside the app that runs a continuous **perceive → reason → act → learn** loop:

1. **Perceive** — consented stream of the user's transaction metadata → trigger engine.
2. **Detect moment** — an adoption opportunity fires (idle cash, competitor premium leak, salary
   jump, contextual spend like travel/electronics).
3. **Reason** — the agent (LLM core) pulls the matching product + honest comparison from the RAG
   layer, runs it through the **suitability filter**, decides whether/what to surface.
4. **Act** — renders a vernacular/voice nudge + **explainability card**; on opt-in, co-pilots the
   real in-app journey with guided highlights.
5. **Learn** — outcome (adopted / skipped / escalated-to-human) tunes trigger thresholds + timing.

### Non-negotiable design principles (these ARE the product)
- **Trust-first, not sales-first.** Recommend only the *simplest* product that matches the
  trigger. **Hard-block** insurance-cum-investment products (ULIPs) and anything unsuitable.
- **Radical transparency.** Always show: the trigger, honest math *including charges/fees*,
  what's NOT covered, and — for comparisons — a row where the competitor genuinely wins.
- **Consent is first-class.** Explicit, revocable opt-in even to *analyse* data for a category.
  Every nudge has "Skip" and "Talk to a human advisor."
- **Vernacular + voice by default.** Hindi + regional languages; voice for low-literacy users.
- **Agentic, autonomous.** The loop decides *when* and *whether* to act — not a passive chatbot
  waiting for a query.

---

## 5. PROTOTYPE SCOPE (build exactly this for Phase 1)

A working end-to-end demo on **synthetic data**. Three trigger flows, the agent loop, the
explainability card, and a vernacular toggle. No real bank data, no real money movement.

**Flow A — Idle-balance → Sweep FD (investment adoption)**
Detect ₹X sitting idle > N days → nudge with honest projected return vs. savings interest →
co-pilot the FD journey.

**Flow B — Competitor premium leak → honest insurance comparison (THE hero demo)**
Detect a recurring premium paid to a competitor insurer → surface a side-by-side honest
comparison (premium, cover, claim-settlement ratio, exclusions, **one row where competitor
wins**) → "Switch only if it makes sense" + "Talk to a human" → explainability card.

**Flow C — Salary inflow / contextual spend → micro-cover (insurance adoption)**
Detect salary jump or a travel/electronics spend → contextual, consent-based simple cover →
suitability-filtered, transparent.

**Must-have UI elements:**
- The nudge card (vernacular toggle: EN / हिंदी).
- The **"Why am I seeing this?"** explainability card (trigger + honest math + data used).
- The guided in-app walkthrough overlay (coachmarks on a mocked YONO-style screen).
- A consent gate the first time a category is analysed.

**Out of scope for prototype (state explicitly in the deck):** server reliability, real KYC/auth,
real fund movement, production security. Mock these.

---

## 6. Technical architecture

```
                ┌────────────────────────────────────────────────────┐
                │                    FRONTEND (React + Vite)          │
                │  Mocked YONO-style app shell                        │
                │  • Nudge card (EN/HI toggle, voice via Web Speech)  │
                │  • Explainability "Why am I seeing this?" card      │
                │  • Guided walkthrough overlay (coachmarks)          │
                │  • Consent gate                                     │
                └───────────────┬────────────────────────────────────┘
                                │ REST (JSON)
                ┌───────────────▼────────────────────────────────────┐
                │                  BACKEND (FastAPI)                  │
                │                                                     │
                │  1. TRIGGER ENGINE                                  │
                │     • consumes synthetic transaction stream         │
                │     • payee classifier (premium/salary/spend)       │
                │     • rule + threshold detection → "adoption moment" │
                │                                                     │
                │  2. AGENT CORE (perceive→reason→act loop)           │
                │     • Anthropic LLM (claude-sonnet-4-6)             │
                │     • tool-calling: query_rag, check_suitability,   │
                │       build_comparison, draft_nudge                 │
                │                                                     │
                │  3. RAG LAYER (grounding / anti-hallucination)      │
                │     • vector store (FAISS local) over product docs, │
                │       fee schedules, policy wordings                │
                │     • embeddings: sentence-transformers (local)     │
                │                                                     │
                │  4. SUITABILITY FILTER (hard rules)                 │
                │     • blocks ULIPs / unsuitable / over-budget       │
                │                                                     │
                │  5. XAI / EXPLAINABILITY builder                    │
                │     • assembles trigger + honest math + data-used   │
                │                                                     │
                │  6. FEEDBACK STORE (sqlite)                         │
                │     • adopted/skipped/escalated → tune thresholds   │
                └─────────────────────────────────────────────────────┘
```

**Agent loop detail (the "agentic" part judges want):** the agent is given the detected event +
user profile and a set of tools. It autonomously decides: is this worth interrupting the user?
which product? does it pass suitability? what's the honest framing? It can choose to *do nothing*
(suppress a low-value or recently-skipped nudge). Log every decision for the demo.

---

## 7. Tech stack

| Layer | Choice | Notes |
|---|---|---|
| Backend | Python 3.11+, FastAPI, uvicorn | |
| Agent core | `anthropic` SDK, model `claude-sonnet-4-6` | tool-calling loop |
| Vector store | FAISS (`faiss-cpu`) | local, no key |
| Embeddings | `sentence-transformers` (e.g. `all-MiniLM-L6-v2`) | local, no key |
| Payee classifier | rules + embeddings (cosine sim to category prototypes) | upgrade path: small trained model |
| Feedback/state | SQLite | |
| Frontend | React + Vite + Tailwind | mocked app shell + overlays |
| Vernacular | LLM handles Hindi/regional natively | no separate translation API |
| Voice | Browser Web Speech API (TTS + optional STT) | free, no key |
| Synthetic data | generated locally (see Section 9) | no external dependency |

---

## 8. Secrets, API keys & MCP servers

### Required
- **`ANTHROPIC_API_KEY`** — the only mandatory secret. Powers the agent reasoning core.
  Put it in `.env` (gitignored): `ANTHROPIC_API_KEY=<paste-key-here>`

### Optional (upgrades, not needed for a working demo)
- `VOYAGE_API_KEY` — only if you want higher-quality embeddings than local sentence-transformers.
- `PINECONE_API_KEY` — only if you want a hosted vector DB instead of local FAISS. Not needed for
  a single-user demo.

### MCP servers
For a **self-contained prototype, no external MCP server is required** — all data is synthetic and
local. Do not wire real banking connectors; it adds risk and zero demo value. Optional, only if a
specific stretch demo calls for it:
- A notifications MCP (e.g. Slack/email) *could* be used to demo "nudge delivered out-of-app,"
  but in-app rendering is cleaner and recommended instead.

> **Guardrail:** never connect this prototype to real customer financial data or real MCP
> banking/payment connectors. Synthetic data only. No real money or PII.

### `.env.example` to generate
```
ANTHROPIC_API_KEY=
# Optional:
# VOYAGE_API_KEY=
# PINECONE_API_KEY=
```

---

## 9. Synthetic data spec

Generate a local dataset so the demo is deterministic and reproducible.

**Transaction record schema:**
```json
{
  "txn_id": "string",
  "timestamp": "ISO-8601",
  "amount": "number (negative=debit, positive=credit)",
  "payee_name": "string (e.g. 'HDFC LIFE PREMIUM', 'ACME CORP SALARY', 'MAKEMYTRIP')",
  "payee_category_truth": "premium|salary|merchant|transfer|bill",
  "channel": "UPI|NACH|IMPS|card",
  "balance_after": "number"
}
```

**Seed personas (so each demo flow has a clean trigger):**
- *Persona 1 — Idle Saver:* large balance, only UPI debits, ₹40k idle 90+ days → Flow A.
- *Persona 2 — Premium Leaker:* recurring ₹1,240/mo to a competitor life insurer → Flow B.
- *Persona 3 — New Earner:* recent salary jump + a MakeMyTrip spend → Flow C.

**RAG corpus to author (synthetic but realistic):** 8–12 short docs — SBI-style FD rates,
SBI Life/SBI General simple product summaries with fees + exclusions, a couple of competitor
fact-sheets for the comparison, and a fee-schedule doc. These ground the "honest math" so the LLM
cannot fabricate numbers.

---

## 10. Build plan / milestones

1. **Scaffold** — repo, `.env.example`, FastAPI skeleton, React shell, synthetic data generator.
2. **Trigger engine** — ingest synthetic stream, payee classifier, fire "adoption moment" events
   for the 3 personas.
3. **RAG layer** — author corpus, embed, FAISS index, `query_rag` tool.
4. **Suitability filter** — hard rules (block ULIP, block over-budget, block recently-skipped).
5. **Agent core** — Anthropic tool-calling loop: perceive event → reason → act/suppress. Log
   every decision.
6. **Explainability builder** — assemble trigger + honest math + data-used card payload.
7. **Frontend flows** — nudge card, EN/HI toggle, voice, walkthrough overlay, consent gate, XAI
   card. Wire to backend.
8. **Feedback loop** — record adopted/skipped, show threshold adjusting (closes the "learn" loop).
9. **Polish + demo script** — make the 3 flows run cleanly for the video.

---

## 11. Guardrails / what NOT to build

- No real PII, no real accounts, no real money movement — **synthetic data only**.
- Never recommend a ULIP / insurance-cum-investment product (auto-block).
- Never recommend a product that fails the suitability filter, even if asked.
- The LLM must not state any premium/return/fee that isn't grounded in the RAG corpus.
- Always include "Skip" and "Talk to a human advisor"; consent is revocable.
- Don't claim to fix reliability/auth/server issues — those are framed as context only.

---

## 12. Demo script (≤3 min)

1. **(0:00) Problem** — one line: 85M YONO users, most touch only UPI; deeper features undiscovered
   and the insurance channel is distrusted due to mis-selling.
2. **(0:25) Flow B hero** — Premium Leaker persona opens app to pay UPI. Saarthi card slides up in
   Hindi: "We noticed ₹1,240/mo going to [competitor]. Want a 30-sec honest comparison?" →
   side-by-side incl. the row where the competitor wins → "Talk to a human / Skip."
3. **(1:20) Explainability** — tap "Why am I seeing this?" → trigger + honest math + data used +
   "this is guidance, not a sale."
4. **(1:50) Flow A** — Idle Saver: idle ₹40k → sweep-FD nudge → guided walkthrough completes.
5. **(2:20) The reframe** — narrate: this moves the sale from a coercive human channel to a
   transparent, consented, suitability-filtered digital one → lifts adoption AND removes the
   mis-selling risk SBI is under regulatory pressure to fix.
6. **(2:45) Scale** — same framework powers all 100+ YONO journeys; white-labelable to other banks.

---

## 13. Sources (for the Problem slide / verification)

Voice-of-customer and market facts above are drawn from:
- App Store / Play Store YONO reviews (UX, UPI failures, off-screen buttons, beneficiary crash).
- Samsung community forums (dual-SIM/eSIM registration, SMS verification failures).
- Tribune / Khaleej Times / Zawya / MySmartPrice — #sbidown outage coverage and user reactions.
- yogi.systems — "Something went wrong" chronic-error grievance writeup.
- pratiksurkar21.substack.com — YONO SWOT (poor UX, logs-off, Bharat exclusion).
- understandingnuances.substack.com — Groww UX teardown ("give you less").
- Business Standard — JanNivesh ₹250 SIP also on Groww/Paytm/Zerodha; mis-selling complaint data.
- topcashbackcard.com / oneinsure.com — SBI insurance mis-selling complaint procedures + cases.
- thekanal.in — SBI internal directive to curb mis-selling; ₹6 lakh forced-policy case.
- The Wire / Business Standard — Rajasthan pensioners duped into SBI Life policies.
- Zopper / ITIJ — 91% of Indian account-holders open to transaction-based insurance offers.
- coinlaw.io / 3ieimpact.org — UPI vernacular + rural/women smartphone-access gaps.
- MatrixBCG / Business Standard — YONO scale (85M users, 50% target, multilingual, 100+ journeys,
  ~₹100 cr/quarter fee income).

> Paraphrase these in the deck; do not quote at length. Verify any number you put on a slide.

---

*End of context. Build the Prototype Scope (Section 5) using the architecture (Section 6) and the
guardrails (Section 11). Keep the agent loop visibly autonomous and the transparency card central
— those are the two things that win this.*
