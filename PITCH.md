# Saarthi — Pitch & Talking Points

**Agentic adoption copilot for YONO. Trust-first, not sales-first.**
SBI Hackathon @ GFF 2026 · "AI & Emerging Tech" · Digital Adoption track.

---

## The one-liner

> Saarthi is an autonomous **perceive → reason → act → learn** agent inside YONO that watches a
> user's *own* transactions, detects high-value adoption moments, and surfaces **just-in-time,
> vernacular, explainable** nudges — moving the sale from a coercive human channel to a
> transparent, consented, suitability-filtered digital one.

---

## The reframe that wins the room

Adoption of insurance and investments isn't broken from lack of demand — **91% of Indian
account-holders are open to transaction-based offers.** It's broken because the **channel** is
distrusted. Two parallel wounds:

1. **Insurance — the trust wound.** Bancassurance is the most-complained-about channel
   (12,000+ mis-selling complaints in a single year); SBI is already under regulatory pressure to
   curb it. People have learned to fear the pitch.
2. **Investing — the self-dealing wound.** YONO's investing experience feels **narrow and
   SBI-skewed** — it foregrounds SBI's own products. Anyone wanting real choice + a clean UI just
   leaves for Groww/Zerodha. YONO has **no exclusivity moat** and loses on experience.

**Saarthi's answer to both is the same: honesty as the moat.** We don't out-pitch the salesman or
out-breadth Groww. We become the one thing neither will build — a trusted, agentic guide.

---

## The investment-breadth unlock (the strong version)

The naïve fix — "list more products, be like Groww" — dilutes SBI's own fee income and needs no AI.
The **strong** play:

|                       | **No guidance**            | **Honest agentic guidance** |
|-----------------------|----------------------------|------------------------------|
| **Narrow shelf**      | Old YONO (self-dealing)    | — (not credible)             |
| **Whole-market shelf**| Groww / Zerodha            | **YONO + Saarthi** ✅        |

**Breadth is the precondition that makes honest guidance credible.** Once YONO lists the whole
market, the "self-dealing" objection dies — so when Saarthi *does* surface an SBI fund with the
honest math, it's *believed*. Neutrality earns trust; trust earns the flow. SBI still earns
distribution commission across all AMCs and wins outright where its product is genuinely best
(JanNivesh ₹250 SIP, low-cost index funds). **"Open the shelf so the honest guide is believed" —
not "sell less of your own."** In the demo, every SBI-product nudge already carries the neutrality
line: *you're seeing this because it fits you, not because it's ours.*

**Shown live, not just claimed.** The New Earner flow demonstrates this concretely: a salary jump opens
a "Markets — the whole shelf" screen listing SBI funds **and** UTI / Parag Parikh / HDFC, plus non-SBI
stocks — with an amber "where a non-SBI option wins" box surfacing the cheaper index fund and the
higher-returning flexi-cap. Every figure is grounded in the corpus and labelled illustrative.

---

## Mapped to the four judging criteria

**1. Innovation.** The mis-selling/​self-dealing reframe. Saarthi is **mis-selling remediation
disguised as an adoption engine** — radical transparency (the honest comparison literally shows a
row where the competitor wins), hard suitability filter (ULIPs auto-blocked), consent-first.

**2. Technical feasibility.** A *working* prototype, not slideware. Real Anthropic tool-calling
agent loop (`query_rag → check_suitability → build_comparison → emit_decision`) with a deterministic
fallback; FAISS-free grounded RAG over a cited corpus; 25 passing tests; deployed on Vercel. The
decision log shows the autonomy live.

**3. Business potential.** YONO earns ~₹100 cr/quarter in fee income from subsidiary
insurance/MF products. Saarthi lifts adoption across **three dimensions** — products (FD, term,
micro-cover), platform features (Bill Pay → AutoPay → Credit Score ladder), and engagement
(subscriptions → goals) — *and* de-risks the regulatory mis-selling exposure SBI is already
scrambling to fix. Activating a dormant digital user costs a fraction of acquiring a new one.

**4. Scalability.** One reusable framework. **Mission Control** in the demo shows the same loop
running autonomously across every user at once — and it's reusable across YONO's 100+ planned
journeys, white-labelable to any bank.

---

## What's deliberately honest (pre-empt the skeptic)

- **Synthetic data only** — no real PII, accounts, or money movement (stated up front).
- **No fabricated numbers** — every premium/rate/fee is grounded in the cited corpus.
- **We don't fix reliability/auth** — those are framed as *causes* of dormancy, not our claim.
- **We never recommend a ULIP** — auto-blocked by the suitability filter, even if asked.

---

## The 30-second close

"Saarthi turns SBI's biggest liabilities — a distrusted insurance channel and a narrow,
self-dealing investment shelf — into its differentiator. By being the only bank super-app with an
honest, agentic, consent-first guide, YONO lifts adoption *and* removes the mis-selling risk it's
under pressure to fix. Same engine, 100+ journeys, any bank."
