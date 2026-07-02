# GFF 2026 Hackathon — Submission Form (final copy)

> Copy-paste these into the portal. Branding: **Diya** everywhere (matches deck, app, video).
> If the portal has locked the title as "Saarthi", stop and re-brand assets instead — do not submit mixed branding.

---

**Theme:** Agentic AI & Emerging Tech

**Problem Statement:** Digital Adoption

**Project Title:**
Diya — An Agentic Adoption Copilot for YONO

**Team details:**
Pratham Garg, Thapar Institute of Engineering & Technology

---

## Brief description of the idea

Diya is an agentic AI copilot inside YONO that turns dormant digital users into active ones — through transparency, not the push-marketing that has eroded trust in bank-sold products. Most of YONO's 85M+ users never go beyond UPI and balance-checks. Diya runs an autonomous perceive→reason→act→learn loop over a user's own transaction patterns to detect "adoption moments" and acts on two fronts:

• Product adoption — idle balance → sweep-FD; a premium leaking to a competitor → an honest side-by-side comparison (including a row where the competitor wins and a "do nothing" column); a salary jump or contextual spend → a simple, consent-based, suitability-filtered cover (ULIPs hard-blocked).

• Platform adoption — detects "feature blind spots" (e.g., paying electricity via another app while YONO Bill Pay sits unused) and guides first-time usage via an adoption ladder that unlocks the next relevant feature each time.

What makes Diya different is its trust architecture. It doesn't just sell honestly — it can un-sell: a reverse mis-selling detector flags unsuitable products the user already owns (e.g., a ULIP sold to a low-income customer) and shows honest exit-vs-stay math within the free-look/surrender window — the bank's own agent remediating its own past mis-sale. Every recommendation must first survive a devil's-advocate AI that argues against it: strong objections suppress the nudge entirely; weak ones are printed on the explainability card (trigger, honest math including fees, what's not covered, plus "skip" and "talk to a human"). Diya may interrupt a user at most 4 times a month — a visible attention budget where silence is a logged decision. High-value adoptions by elderly users require a family member's co-approval on a second device (Sahayak mode), and every decision — surfaced or suppressed — is appended to a hash-chained, regulator-ready compliance audit trail.

A vernacular voice copilot lets users simply speak — in Hindi/regional languages — and Diya co-pilots the task, highlighting exactly where to tap; this reaches the half of SBI's base excluded by app complexity and literacy. Net effect: the insurance/investment sale moves from a coercive human channel to a transparent, consented, auditable digital one — mis-selling remediation disguised as an adoption engine.

## Proposed solution — Business model / commercial potential

Diya grows YONO's existing fee engine while de-risking it. YONO already earns ~₹100 cr/quarter in fee income from selling subsidiary insurance and mutual-fund products; modest attach-rate lifts compound across 85M+ users. Three value levers:

• Activation — reactivating a dormant digital user costs a fraction of acquiring a new one (direct cost-to-income win); the platform-adoption flows raise feature adoption and DAU.

• Cross-sell uplift — trust-first, contextual nudges raise insurance/MF/FD attach where push campaigns fail. Subscription management — among the most-wanted mobile-banking features globally — is a high-demand engagement hook.

• Compliance as an asset — banks receive the most mis-selling complaints of any channel, and SBI is under regulatory pressure to fix it. Diya's hash-chained suitability audit trail gives SBI a per-recommendation, regulator-ready answer for RBI/IRDAI, and the reverse mis-selling detector actively remediates legacy risk — converting a liability into a differentiator no competitor bank offers.

Scales horizontally across YONO's 100+ planned journeys (Diya is the adoption layer for each new feature) and white-labels to other banks as an agentic Digital Adoption Platform.

## Technology stack details

• Backend: Python, FastAPI

• Agent core: Anthropic LLM with a tool-calling perceive→reason→act loop, plus an adversarial second pass (devil's-advocate agent) that must clear every recommendation before it surfaces

• Grounding: RAG over product docs + fee schedules with a FAISS vector store + local embeddings (figures never fabricated)

• Suitability & governance: rule-based hard-blocks (ULIPs/unsuitable plans), attention-budget governor (max 4 nudges/user/month), guardian co-consent state machine for assisted users

• Compliance: SHA-256 hash-chained audit log of every agent decision (surfaced or suppressed) with a chain-verify endpoint and a Compliance view in Mission Control

• Explainability (XAI) module: assembles the "why am I seeing this" card, including the devil's-advocate objection and a "do nothing" baseline in every comparison

• Voice copilot: STT + TTS via Sarvam AI (Saarika/Bulbul — 22 Indian languages, Hinglish) and/or Bhashini (Govt-of-India language DPI, NPCI UPI Voice); browser Web Speech for the English demo

• Guided walkthrough: React coachmark/overlay engine that spotlights the exact UI element to tap and advances on the real user action, with voice narrating each step

• Feedback store: SQLite (adoption-ladder state + learning loop + attention budgets)

• Frontend: React (mocked YONO shell), EN/हिंदी toggle, consent gate

• Data: synthetic transactions only — no real PII

## Process flow / architecture

Diya runs a continuous autonomous agent loop:

Perceive — consented transaction signals → trigger engine (idle balance, competitor premium, salary inflow, contextual spend, feature blind-spot, and unsuitable products the user already holds).

Reason — grounds the recommendation via RAG, runs it through the suitability filter, then cross-examines it: a devil's-advocate agent argues against the nudge (strong objection → suppressed), and the attention-budget governor decides whether the moment is worth one of the user's 4 monthly interruptions. Choosing silence is a first-class, logged decision.

Act — surfaces a vernacular nudge + explainability card (including the surviving objection and a "do nothing" column); on opt-in, co-pilots the in-app journey with a voice-narrated coachmark walkthrough. Adoptions above a threshold for assisted users block until a guardian co-approves on a second device.

Learn — outcome (adopted/skipped/escalated) tunes triggers and unlocks the next feature on the adoption ladder. Every decision in the loop is appended to a hash-chained compliance audit trail, verifiable end-to-end.

Flows: Feature Discovery (platform adoption), Insurance honest-comparison + Reverse mis-selling remediation (trust-first product adoption), Subscription Saver (engagement→adoption bridge), Idle→Goal→FD/SIP (investment adoption), with voice as the cross-cutting Bharat layer. (Full architecture diagram in the deck.)

---

## Remaining fields

**Upload your idea deck:** `Diya-Deck-v2.pptx` — upload AFTER final assembly (screenshots + team name being injected once the feature build lands).

**Demo video link:** optional field — if you record one later, `video/FINAL_VIDEO_SCRIPT.md` + `video/SHOT_LIST.md` have the full plan; upload to YouTube as *Unlisted* and paste the link. Otherwise leave blank (the field is "If any").

**GitHub repository link:** https://github.com/prathamgarg1103/sbihack.git
⚠ Before submitting: (1) commit + push today's work (new features, deck, video folder are currently uncommitted), (2) make sure the repo is public or judges can't open it, (3) confirm `.env` is not committed (only `.env.example`).
