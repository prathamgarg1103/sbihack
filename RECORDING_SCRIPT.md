# Diya — Video Recording Script (read-along)

> Word-for-word narration for your MP4. **[CAM]** = you on camera · **[SLIDE n]** = show that slide ·
> **[SCREEN]** = share the live app (saarthi-nu.vercel.app). Target **~4 min**. Speak slowly; pause at the
> bold lines. Numbers in *(italics)* are sourced — they're on the slides too.

---

### 0:00 — Hook  **[CAM]**
"Hi, we're **Team Diya**. SBI's YONO has **85 million users** — but most only ever tap UPI and
balance-check. The features that actually help people, and that earn SBI money, go undiscovered. And
the one channel that sells them — insurance and investments — people have learned to *distrust*.
**Diya is an agentic AI copilot that fixes both.**"

### 0:22 — The problem  **[SLIDE: The Problem]**
"Adoption here isn't a *demand* problem — it's a *trust* problem. Two wounds. **One:** bank insurance
is the most-complained channel — over *12,000 mis-selling complaints in a single year* — and SBI is
already under regulatory pressure to fix it. **Two:** YONO's investing shelf is narrow and pushes
SBI's own products, so anyone who wants real choice leaves for Groww or Zerodha. Yet *91% of Indian
account-holders are open to transaction-based offers.* Demand is fine. The channel is broken."

### 0:50 — The reframe  **[SLIDE: The Reframe]**
"So we're not pitching cross-sell. We're pitching **mis-selling remediation — disguised as an
adoption engine.** Diya moves the sale from a coercive human channel to a transparent, consented,
suitability-filtered, explainable digital one. **Honesty becomes the moat.**"

### 1:05 — What Diya is  **[SLIDE: Meet Diya / the loop]**
"Diya runs a continuous, autonomous loop — **perceive, reason, act, learn** — over a user's *own*
consented transactions. It's a real Claude tool-calling agent: it decides *whether*, *what*, and
*when* to nudge — and it can choose to stay silent rather than nag. Every step is logged, so you can
watch it reason. Let me show you the live prototype."

### 1:25 — DEMO: the hero, honest comparison  **[SCREEN: pick "Premium Leaker"]**
"This user pays a recurring premium to a competitor insurer. Before Diya even *analyses* that, it
asks consent — in Hindi. *(allow)* It spots ₹1,240 a month leaving, and offers an **honest
comparison.** *(tap it)* Here's the proof this isn't a sale: Diya shows the row where the
**competitor wins** — a higher claim-settlement ratio — right next to where SBI is cheaper. Every
figure is grounded in a cited corpus; nothing invented. And the off-ramp is always **'talk to a
human.'** *(tap 'Why am I seeing this?')* Full transparency: the trigger, the exact data used."

### 2:05 — DEMO: open-shelf investing  **[SCREEN: pick "New Earner"]**
"Here's the investment story. This user's salary just jumped. *(allow → 'See investment options')*
Instead of pushing SBI funds, Diya opens the **whole market** — SBI funds *and* UTI, Parag Parikh,
HDFC, plus stocks beyond SBI. And it points to where a **non-SBI option wins** — a cheaper index
fund, a higher-returning flexi-cap. **Breadth is what makes the honest guidance believable** — and
SBI still earns distribution on every fund."

### 2:35 — DEMO: it learns + runs at scale  **[SCREEN: Explorer → walkthrough; then Mission Control toggle]**
"Diya also *learns*. The Explorer never used Bill Pay — Diya guides them through it once, then climbs
an **adoption ladder** to suggest AutoPay next. And this — **Mission Control** — is the agent running
autonomously across *every* user at once, deciding per person: nudge, hold back, or stay silent. One
loop, reusable across YONO's 100-plus planned journeys."

### 3:05 — Business  **[SLIDE: Business]**
"The business case: YONO earns about *₹100 crore a quarter* distributing its subsidiaries' products.
Diya lifts that across **three dimensions** — product, platform, and engagement — *and* removes the
mis-selling risk SBI must fix. Reactivating a dormant user costs a fraction of acquiring a new one."

### 3:25 — Feasibility  **[SLIDE: Feasibility]**
"And it's real — not slideware. A live Claude agent loop, grounded retrieval so it can't invent
numbers, a hard suitability filter that auto-blocks ULIPs, a learning store — *26 passing tests*,
deployed live on Vercel, synthetic data only."

### 3:45 — Close  **[CAM, then SLIDE: Close + QR]**
"Diya turns SBI's two biggest liabilities — a distrusted insurance channel and a narrow investing
shelf — into its **differentiator.** Same framework, 100-plus journeys, white-label-able to any bank.
It's live right now — scan the code to try it. Thank you."

---

## Recording tips
- **Two takes that cut together well:** record the talking-head bits *(CAM)* separately from the
  screen capture *(SCREEN)*, then stitch. Saves you fumbling between camera and app.
- **For the "LLM live" badge** in the demo, run locally with an `ANTHROPIC_API_KEY` in `.env`; the
  deployed site shows "rules" until you add the key in Vercel. Both look clean — keep it consistent.
- **Reset learning** between demo personas (button in the decision panel) so the learn beat is clean.
- Keep the browser at 100% zoom, hide the bookmarks bar, 1080p.
- If you only have 3 minutes: drop the open-shelf demo *(2:05)* and the learn/Mission-Control beat
  *(2:35)* down to one sentence each.
