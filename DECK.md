# Saarthi — Pitch Deck Content (Canva-ready)

> Drop each slide into your Canva template. Each block has **ON-SLIDE** (exact text that appears),
> **SPEAKER NOTES** (what you say), and **VISUAL** (what to put on the slide). 14 slides + 2 backup.
> Total talk-time ≈ 4–5 min; pairs with the 3-min demo video (see `VIDEO_SCRIPT.md`).

## Design system (so the deck matches the product)
- **Colors:** ink `#0B1F3A` · SBI blue `#1755C4` · sky `#3D8BFF` · mint `#0FB98A` (good/adopt) ·
  amber `#F5A524` (honesty/caution) · paper `#F4F6FB`.
- **Font:** Inter (or any clean sans). **Logo mark:** a ✦ in a blue→mint gradient circle.
- **Tone:** confident, honest, restrained. White space > clutter. One idea per slide.
- **Numbers carry a tiny source footnote** — judges trust cited figures (verify before final print;
  sources listed on the last slide).

---

## Slide 1 — Title

**ON-SLIDE**
- **Saarthi**
- The Agentic Adoption Copilot for YONO
- *Trust-first AI that turns dormant users into confident ones.*
- [Team name] · [Member names] · SBI Hackathon @ GFF 2026 — AI & Emerging Tech

**SPEAKER NOTES:** "We're Saarthi — an agentic AI copilot that lives inside YONO and fixes the two
things stopping people from going deeper: discovery and trust."

**VISUAL:** YONO-blue→sky gradient background, the ✦ mark, a faint phone mockup on the right showing
a nudge card. Big product name, small everything else.

---

## Slide 2 — The problem (the hook)

**ON-SLIDE**
- **85 million users. Most only tap UPI.**
- YONO already has investing, insurance, bill-pay, credit score — but the deep journeys go
  *undiscovered*, and the products that earn revenue are sold through a channel people *distrust*.

**SPEAKER NOTES:** "85 million registered users — and most never go past UPI and balance-check. The
deeper features that actually help people, and that earn SBI fee income, stay invisible — or worse,
distrusted."

**VISUAL:** An iceberg — tip labelled "UPI · Balance check (what users touch)", the huge submerged
mass labelled "Investing · Insurance · Bill Pay · Credit Score · 100+ journeys". 85M as a big stat.

---

## Slide 3 — Two wounds

**ON-SLIDE**
- **Adoption isn't a demand problem. It's a trust problem.**
- **Wound 1 — Insurance:** bancassurance is the most-complained-about channel — 12,000+ mis-selling
  complaints in a single year. SBI is already under regulatory pressure to fix it.
- **Wound 2 — Investing:** YONO's shelf feels narrow & SBI-skewed → users leave for Groww/Zerodha.
- *91% of Indian account-holders are open to transaction-based offers. The channel is broken — not
  the demand.*

**SPEAKER NOTES:** "Two wounds. Insurance has a trust wound — banks are the most-complained channel
for mis-selling. Investing has a self-dealing wound — YONO mostly shows SBI's own products, so
people leave for Groww. But 91% are open to these offers. Demand is fine. The *channel* is broken."

**VISUAL:** Two cards side by side (amber accent). Left: a broken-handshake / complaint icon + "12,000+".
Right: app icons (Groww/Zerodha) with an arrow of users leaving YONO. "91%" as a banner across the bottom.

---

## Slide 4 — The reframe (the winning idea)

**ON-SLIDE**
- **Not cross-sell. Mis-selling remediation — disguised as an adoption engine.**
- Saarthi moves the sale from a **coercive human channel** → a **transparent, consented,
  suitability-filtered, explainable digital one.**
- **Honesty is the moat.**

**SPEAKER NOTES:** "Here's the reframe that wins the room. We're not pitching cross-sell. We're
pitching mis-selling remediation — something SBI is *already scrambling to deliver* — and dressing
it as an adoption engine. We move the sale off the coercive human channel onto an honest, opt-in,
explainable digital one. Honesty becomes the moat."

**VISUAL:** A single bold arrow: "Coercive human agent 😠" → "Honest AI copilot ✦". Strike-through the
word "Cross-sell", replace with "Remediation".

---

## Slide 5 — Meet Saarthi

**ON-SLIDE**
- **An agent that reads your *own* transactions and co-pilots the journey you'd never find alone.**
- A continuous **perceive → reason → act → learn** loop.
- Every nudge ships with: the trigger · the honest math (incl. charges) · what's *not* covered ·
  "Talk to a human." In your language. Read aloud.

**SPEAKER NOTES:** "Saarthi watches a user's own consented transaction patterns, spots a high-value
moment, and co-pilots them through it — in Hindi or English, by voice if they can't read. Every
nudge is honest by construction."

**VISUAL:** The 4-stage loop as a circle (perceive→reason→act→learn) with a phone showing a nudge card
in Hindi at the centre.

---

## Slide 6 — The agentic core (the judges' #1 ask)

**ON-SLIDE**
- **Autonomous — not a chatbot waiting for a query.**
- A live **Claude tool-calling loop** decides *whether, what, and when* — and can choose to **do
  nothing**.
- Tools: `query_rag` (grounding) · `check_suitability` (hard rules) · `build_comparison` (honest).
- Guardrails: **ULIPs auto-blocked** · states **no number it didn't retrieve** · **consent-first**.
- *Every decision is logged and visible.*

**SPEAKER NOTES:** "The agentic part the judges asked for is real, not bolted on. A Claude
tool-calling loop autonomously decides whether to even interrupt you, which product fits, whether it
passes the suitability filter — and it logs every step so you can watch it reason. It will suppress
a nudge rather than nag. That restraint *is* the product."

**VISUAL:** Screenshot of the **Agent Decision Loop** panel (PERCEIVE → REASON `query_rag()` /
`check_suitability()` → ACT) with the "LLM live" badge circled. Show the 3 tool chips + the 3 guardrails.

---

## Slide 7 — Five journeys, one framework

**ON-SLIDE** (table)
| Flow | Trigger | Honest action |
|---|---|---|
| **A** | ₹47k idle 150+ days | Sweep-FD vs 2.7% savings — the honest math |
| **B** ★ | ₹1,240/mo to a competitor insurer | Side-by-side honest comparison |
| **C** | Salary jump ₹35k→₹55k | Open-shelf investing — the *whole* market |
| **D** | Pays bills in another app | Guided in-YONO walkthrough + adoption ladder |
| **S** | Subscription renews in 3 days | Pause → invest the savings toward a goal |

**SPEAKER NOTES:** "Five journeys today, all on one reusable framework — product adoption, platform
adoption, and engagement. Flow B is our hero; Flow C is the investment story I'll show you."

**VISUAL:** Five mini phone screens in a row, B highlighted with a ★. Keep the table clean.

---

## Slide 8 — The hero: the honest comparison (Flow B)

**ON-SLIDE**
- **We show the row where the competitor wins.**
- Premium · cover · **claim-settlement ratio** · exclusions — side by side. SBI is cheaper; the
  competitor's claim ratio is higher. We say so.
- *"Switch only if it makes sense."* Every figure grounded in a cited corpus. "Talk to a human"
  always one tap away.

**SPEAKER NOTES:** "This is what trust-first looks like. When Saarthi compares an SBI policy to the
competitor the user already pays, it shows the row where the *competitor* wins — a higher claim
ratio — right next to where SBI is cheaper. No invented numbers. That honesty is exactly what the
mis-selling channel never gave them."

**VISUAL:** Screenshot of the comparison screen with the amber "Where [competitor] wins" box circled.

---

## Slide 9 — The investment-breadth unlock

**ON-SLIDE**
- **Open the shelf so the honest guide is believed.**
- 2×2:
  - Narrow shelf + No guidance → *nobody*
  - Narrow shelf + Guidance → **Old YONO** (feels self-dealing)
  - Whole-market shelf + No guidance → **Groww / Zerodha**
  - **Whole-market shelf + Honest guidance → YONO + Saarthi ✅**
- Listing competitors *kills* the self-dealing objection — so an SBI-fund recommendation is believed.
  SBI still earns distribution across all AMCs, and wins where its product is genuinely best.

**SPEAKER NOTES:** "Our answer to the investing wound isn't 'be like Groww' — that dilutes SBI's fees
and needs no AI. It's this: breadth is the *precondition* that makes honest guidance credible. List
the whole market, and when Saarthi *does* point you to an SBI fund with the honest math, you believe
it — because it just as readily flagged a cheaper UTI index fund. In our demo, the New Earner opens a
real shelf with SBI *and* competitor funds and stocks. Neutrality earns trust; trust earns the flow."

**VISUAL:** A clean 2×2 matrix, the bottom-right quadrant ("YONO + Saarthi") glowing mint. Small inset:
the "Markets — the whole shelf" screenshot showing SBI + UTI + Parag Parikh + stocks.

---

## Slide 10 — Trust-first by design

**ON-SLIDE**
- **Transparency is the product — not a feature.**
- "Why am I seeing this?" card (trigger + data used) · revocable **consent gate** · **Talk to a human**
  · neutrality line ("not because it's ours") · **vernacular + voice** · ULIPs auto-blocked.
- **It learns:** skip a nudge → it backs off. Adopt a feature → the ladder advances to the next.

**SPEAKER NOTES:** "Every guardrail you'd want is first-class: an explainability card, a revocable
consent gate, a human off-ramp, vernacular and voice for Bharat. And it closes the loop — skip a
category and it stops nagging; adopt Bill Pay and it unlocks AutoPay next. The agent adapts to the
person."

**VISUAL:** Three small screenshots: the "Why am I seeing this?" card, the consent gate, and the
adoption ladder (Bill Pay ✓ → AutoPay highlighted).

---

## Slide 11 — Built to scale: Mission Control

**ON-SLIDE**
- **One loop. Every user. 100+ journeys.**
- Mission Control runs the agent **autonomously across the whole base** — nudge, hold back, or stay
  silent, per person.
- The same framework powers YONO's 100+ planned journeys — and is **white-labelable to any bank.**

**SPEAKER NOTES:** "This is the scalability story made visual. Mission Control shows the agent
sweeping every user at once and deciding per person. It's one loop — reusable across the 100+
journeys YONO is planning, and white-labelable to any other bank."

**VISUAL:** Screenshot of the Mission Control feed ("Swept 5 users · 5 nudged · 0 held back —
autonomously") on the dark console.

---

## Slide 12 — Business potential

**ON-SLIDE**
- **Lifts revenue *and* removes risk.**
- YONO earns **~₹100 cr/quarter** in fee income from subsidiary insurance/MF products.
- Saarthi lifts adoption across **3 dimensions** — product, platform, engagement — *and* de-risks the
  mis-selling exposure SBI is under pressure to fix.
- Activating a dormant digital user costs a **fraction** of acquiring a new one.

**SPEAKER NOTES:** "The business case writes itself. YONO already earns around ₹100 crore a quarter
distributing its subsidiaries' products. Saarthi lifts that across three adoption dimensions while
*removing* the regulatory mis-selling risk — and reactivating a dormant user is far cheaper than
acquiring a new one. We grow the number and de-risk it at the same time."

**VISUAL:** Two upward arrows — "Fee income ↑" (mint) and "Mis-selling risk ↓" (amber) — over a "₹100
cr/quarter" anchor stat.

---

## Slide 13 — Technical feasibility

**ON-SLIDE**
- **A working prototype — not slideware.**
- **Agent:** Claude (`claude-sonnet-4-6`) tool-calling loop + deterministic fallback.
- **Grounding:** cited RAG corpus (no fabricated numbers). **Guardrail:** hard suitability filter.
  **Learn:** SQLite outcome store.
- **Stack:** FastAPI · React/Vite/Tailwind. **26 tests passing.** Deployed on Vercel.
- Only secret required: `ANTHROPIC_API_KEY`. **Synthetic data only — no real PII or money.**

**SPEAKER NOTES:** "It runs today. A real Claude agent loop, a grounded retrieval layer so it can't
invent numbers, a hard suitability filter, a learning store — FastAPI and React, 26 passing tests,
live on Vercel. One API key to run it; everything else is local and free; all data synthetic."

**VISUAL:** A simple architecture diagram — Frontend (phone) → FastAPI → [Trigger engine · Agent loop ·
RAG · Suitability · Feedback] → Claude. Logos for the stack.

---

## Slide 14 — Close

**ON-SLIDE**
- **Saarthi turns SBI's biggest liabilities — a distrusted insurance channel and a narrow investing
  shelf — into its differentiator.**
- Honest, agentic, consent-first. Lifts adoption. Removes mis-selling risk. Reusable across 100+
  journeys. White-label-ready.
- **Try it live:** saarthi-nu.vercel.app   ·   [QR code]

**SPEAKER NOTES:** "So: Saarthi takes SBI's two biggest liabilities and makes them the reason to
choose YONO. It's live right now — scan the code. Thank you."

**VISUAL:** Big QR to https://saarthi-nu.vercel.app, the tagline, the ✦ mark. Confident, minimal.

---

## Backup Slide A — What we deliberately did NOT build (honesty)
**ON-SLIDE:** No real KYC/auth · no real money movement · no server-reliability claims (those *cause*
dormancy but aren't our job) · we never recommend a ULIP. **Synthetic data only.**
**Use when:** a judge probes scope or guardrails. Shows discipline.

## Backup Slide B — The agent's reasoning, live
**ON-SLIDE:** Full decision-log screenshot with the "LLM live" badge + the tool trace
(`query_rag → check_suitability → build_comparison → emit_decision`).
**Use when:** a judge asks "show me it's really agentic." Open the live app instead if possible.

---

## Sources (footnote bank — cite small on the relevant slides; verify before final)
- YONO scale (85M users, 50% target, ~₹100 cr/quarter fee income, 100+ journeys): MatrixBCG /
  Business Standard.
- Mis-selling complaints (12,000+/yr; banks most-complained channel): topcashbackcard.com /
  oneinsure.com / thekanal.in.
- 91% open to transaction-based offers: Zopper / ITIJ.
- Groww/Zerodha competition & JanNivesh ₹250 SIP also on third-party apps: Business Standard /
  understandingnuances.substack.com.
- Bharat gap (~35% women smartphone ownership; rural UPI ~38%): coinlaw.io / 3ieimpact.org.

> ⚠️ Per our own rule — verify every number before it goes on a printed slide.

---

## Screenshot / asset capture checklist

Capture from the **live site** for crisp, full-res images: open **https://saarthi-nu.vercel.app** in
your browser at 100% zoom (or run locally for the "LLM live" badge). Each row = one image the deck needs.

| # | For slide | Screen | How to reach it | Crop / note |
|---|---|---|---|---|
| 1 | 1, 5 | App hero + nudge | Land on the page; pick **Premium Leaker** → allow consent | The phone + the nudge card (in Hindi) |
| 2 | 6, B-backup | **Agent Decision Loop** | Any persona, after a nudge shows | The right-hand panel: PERCEIVE→REASON→ACT + badge |
| 3 | 8 | **Honest comparison** | Premium Leaker → "See the honest comparison" | Include the amber "Where [competitor] wins" box |
| 4 | 9 | **Markets — the whole shelf** | New Earner → "See investment options" | Show SBI + UTI/PPFAS/HDFC funds + the stocks list |
| 5 | 10 | "Why am I seeing this?" + consent | Any persona; tap "Why am I seeing this?" | Two shots: consent gate, and the XAI reveal |
| 6 | 10 | Adoption ladder / walkthrough | **Explorer** → "Show me" walkthrough | The coachmark steps + the ladder in the side panel |
| 7 | 11 | **Mission Control** | Top toggle → "Mission Control" | The dark feed: "Swept 5 users · 5 nudged…" |

Tip: for the "LLM live" badge in #2, run locally with `ANTHROPIC_API_KEY` set (the deployed site shows
"rules" until you add the key in Vercel env vars). For the deck, "rules" vs "LLM live" both look clean —
just keep it consistent across shots.
