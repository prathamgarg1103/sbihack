# Saarthi — 3-Minute Demo Video Script

> Recorded walkthrough for the SBI Hackathon (Digital Adoption track).
> Target length **≈ 2:50**. Shot list + voiceover (VO) + exact clicks.

---

## Before you hit record (setup)

1. **Backend** (from `/backend`): `.venv\Scripts\python -m uvicorn main:app --port 8000`
2. **Frontend** (from `/frontend`): `npm run dev` → open `http://localhost:5173`
3. **For the "LLM live" badge** (strongly recommended): put `ANTHROPIC_API_KEY=...` in the repo-root
   `.env`, then restart the backend. The Agent Decision Loop badge flips from **rules → LLM live**
   and the decision log shows real `query_rag` / `check_suitability` / `build_comparison` calls.
4. **Clean slate:** in each persona's decision panel click **reset** (clears learned feedback) so
   the learn-loop beat records cleanly. Start on the **Demo** tab, **Idle Saver** persona.
5. Zoom browser to ~110%, hide bookmarks bar. Record at 1080p.

---

## Scene 1 — The problem (0:00–0:20)

**On screen:** the YONO phone shell (any persona), Saarthi header visible.

**VO:** "YONO has 85 million users — but most only ever touch UPI and balance-check. The deeper
features go undiscovered, and the insurance channel is *distrusted*, because it's been sold by a
coercive, target-driven human machine. Saarthi is an **agentic copilot** that fixes both — by
moving the moment from a sales pitch to honest, just-in-time guidance."

---

## Scene 2 — Flow B, the hero: honest insurance comparison (0:20–1:10)

**Click:** **Premium Leaker** persona (Rahul). A consent gate slides up **in Hindi**.

**VO:** "Rahul pays a recurring premium to a competitor insurer. Before Saarthi even *analyses*
that, it asks permission — consent is first-class."

**Click:** **हाँ, विश्लेषण करें** (Yes, analyse). The nudge appears in Hindi.

**VO:** "It noticed ₹1,240 a month leaving to another insurer, and offers an *honest* comparison —
not a pitch."

**Click:** the primary CTA → the **Honest comparison** opens.

**VO (point at the amber box):** "Here's the proof this isn't a sale: Saarthi shows the row where
the **competitor wins** — a higher claim-settlement ratio — right next to where SBI is cheaper.
Every figure is grounded in a cited corpus; nothing is invented."

**Click:** **Talk to a human advisor first** → confirmation appears.

**VO:** "And the off-ramp is always a real human — *guidance, not a sale.*"

---

## Scene 3 — Explainability + open-shelf neutrality (1:10–1:35)

**Click:** "Not now" → back to the nudge. **Click:** **Why am I seeing this?**

**VO:** "Total transparency: the exact trigger, the data used, and the promise that this is
guidance, not a sale."

**Point at the ⚖️ line:** "And because YONO should list the *whole market*, every product surface
carries this: *you're seeing this because it fits you — not because it's an SBI product.*"

---

## Scene 4 — Flow A + vernacular + voice (1:35–1:55)

**Click:** **Idle Saver** persona → allow consent. Nudge appears (Hindi).

**Click:** the **EN / हिं** toggle to English, then the **🔊** speaker.

**VO:** "₹47,000 sitting idle for 152 days, earning 2.7%. Saarthi nudges a Sweep FD — in the user's
language, and read aloud for low-literacy users. Same trust-first framing."

---

## Scene 5 — New Earner: the open shelf (the investment-breadth proof) (1:45–2:15)

**Click:** **New Earner** persona → allow consent. The nudge (English): *"Your income just grew —
₹35,000 to ₹55,000. Want to put part of your raise to work, across the whole market, not just SBI's
funds?"*

**VO:** "Here's the investment story. YONO's investing has felt narrow and self-dealing — list mostly
SBI's own funds — so people leave for Groww. Watch what Saarthi does instead."

**Click:** **See investment options** → the **Markets — the whole shelf** screen opens.

**VO (point at the count chips + the amber box):** "It lists the *whole market* — SBI's funds *and*
UTI, Parag Parikh, HDFC — plus stocks beyond SBI. And the proof it's honest: Saarthi points you to
the **non-SBI** options that win — a cheaper index fund, a higher-returning flexi-cap. Open the shelf,
and the guidance becomes believable. That's the moat Groww won't build — and SBI still earns on every
fund it distributes."

---

## Scene 6 — The learn loop (2:15–2:35)

**Click:** **Explorer** persona → allow → complete the **guided walkthrough** (Bill Pay coachmarks)
→ **Great**.

**VO:** "Watch it *learn*. The Explorer never used Bill Pay — Saarthi guides them through it once."

**Click:** reselect **Explorer**. Point at the decision log:

**VO:** "Now the agent remembers, advances the **adoption ladder**, and surfaces the next unused
feature — AutoPay. Adoption compounds. (And if a user skips a category, Saarthi backs off instead
of nagging — you can see that in the LEARN step.)"

---

## Scene 7 — Mission Control: autonomy at scale (2:35–2:50)

**Click:** the **Mission Control** tab.

**VO:** "This is the agent running autonomously across *every* user at once — perceiving, reasoning,
and deciding per person: nudge, hold back, or stay silent. One loop, every user — and it's reusable
across YONO's 100-plus planned journeys. That's the scalability story."

---

## Scene 8 — The reframe + close (2:50–3:05)

**On screen:** Mission Control (or the comparison) held.

**VO:** "Saarthi moves the sale from a coercive human channel to a transparent, consented,
suitability-filtered digital one. It lifts adoption across products, platform features *and*
investments — while removing the mis-selling risk SBI is under regulatory pressure to fix. Same
framework, white-labelable to any bank. That's Saarthi."

---

### If asked to show the "agentic" core on camera
Open the **Agent Decision Loop** panel (right of the phone). With a key set it reads **LLM live**
and lists the real tool calls the model made — `query_rag → check_suitability → build_comparison →
emit_decision` — proving the perceive→reason→act loop is genuine, not scripted.

### Backup
The deployed Vercel link is the fallback if anything local hiccups. The deterministic engine looks
identical minus the "LLM live" badge.
