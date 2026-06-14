# Saarthi — Agentic Adoption Copilot for YONO

A trust-first, **agentic** AI adoption copilot that lives inside a mocked YONO
super-app. It watches a user's own (synthetic) transaction patterns, detects
high-value "adoption moments," and surfaces just-in-time, vernacular,
**transparency-first** nudges — every recommendation shipping with an
explainability card and a hard suitability filter.

> Full product context, problem framing and guardrails live in [`CLAUDE.md`](./CLAUDE.md).

---

## Architecture (at a glance)

```
React + Vite + Tailwind  ──/api──►  FastAPI
  mocked YONO shell                  ├─ trigger engine      (payee classify + thresholds)
  nudge / XAI / consent              ├─ agent core          (Anthropic tool-calling loop)
  walkthrough overlay                ├─ RAG layer           (TF-IDF cosine over local corpus)
                                     ├─ suitability filter  (hard rules: ULIP block, budget…)
                                     ├─ XAI builder         (trigger + honest math + data used)
                                     └─ feedback store      (SQLite: adopted/skipped/escalated)
```

The agent runs a **perceive → reason → act → learn** loop and logs every
decision (including *suppressions*) so the autonomy is visible in the demo.

---

## Prerequisites

- Python 3.11+  (developed on 3.14)
- Node 20+ / npm 10+
- An `ANTHROPIC_API_KEY` (the only required secret)

## Setup

```bash
# 1. Secret
cp .env.example .env          # then paste your ANTHROPIC_API_KEY

# 2. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate         # Windows  (use: source .venv/bin/activate on *nix)
pip install -r requirements.txt
python data/generate.py        # writes data/transactions.json (3 personas)

# 3. Frontend
cd ../frontend
npm install
```

## Run (two terminals)

```bash
# Terminal 1 — backend
cd backend
.venv\Scripts\activate
uvicorn main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev                    # http://localhost:5173  (proxies /api -> :8000)
```

Open **http://localhost:5173**. The persona switcher on the left drives the
three demo flows.

---

## Demo personas (synthetic)

| Flow | Persona | Trigger |
|------|---------|---------|
| **A** | Aarti Sharma — *Idle Saver* | ~₹47k sitting idle 90+ days → sweep-FD nudge |
| **B** | Rahul Verma — *Premium Leaker* | recurring ₹1,240/mo to a competitor insurer → honest comparison (hero demo) |
| **C** | Sneha Iyer — *New Earner* | salary jump + MakeMyTrip spend → contextual micro-cover |

---

## RAG note

The retrieval layer uses **TF-IDF cosine similarity** over a small local
corpus — zero API keys, instant install, and identical grounding behaviour for
a ~10-doc corpus. The architecture supports swapping in **FAISS +
sentence-transformers** (or Voyage embeddings) as a drop-in upgrade.

## Guardrails

Synthetic data only · no real money movement · ULIPs auto-blocked · no
ungrounded numbers (every premium/return/fee comes from the corpus) · every
nudge carries "Skip" + "Talk to a human advisor" · consent is revocable.

---

## Build status

- [x] **M1** — scaffold: repo, env, FastAPI skeleton, React shell, synthetic data
- [x] **M2** — trigger engine: payee classifier + threshold detection, `/triggers`, 7 tests
- [x] **M3** — RAG layer: 8-doc grounded corpus + TF-IDF `query_rag`, honest comparison builder
- [x] **M4** — suitability filter: hard rules (ULIP block, budget, recently-skipped), 6 tests
- [x] **M5** — agent core: perceive→reason→act loop with decision log. LLM path
      (`claude-sonnet-4-6` tool-calling) when a key is set; deterministic fallback otherwise
- [x] **M6** — explainability: "Why am I seeing this?" card (trigger + honest math + data used)
- [x] **M7** — frontend flows: nudge card, EN/हिंदी toggle, voice (Web Speech), consent gate,
      honest comparison table. *Pending: coachmark walkthrough overlay.*
- [x] **M8** — feedback loop: SQLite store; a skipped category is suppressed next time, 4 tests
- [~] **M9** — polish + demo script (below). *Pending: LLM path needs a key to verify live.*

**17 tests passing.** Set `ANTHROPIC_API_KEY` in `.env` to upgrade the agent from the
deterministic fallback to the live `claude-sonnet-4-6` tool-calling loop.

---

## Demo script (~3 min)

1. **Premium Leaker (Flow B — hero).** Select the persona → consent gate → "Yes,
   analyse" → the nudge: *"You pay ₹1,240/mo to HDFC Life. Want an honest
   comparison?"* Tap **"See the honest comparison"** → side-by-side table where
   SBI wins on premium but **HDFC wins the claim-settlement-ratio row**, ₹3,080/yr
   saving, verdict, and the four cited source docs. Watch the **agent decision
   loop** panel log every step.
2. **Explainability.** Tap **"Why am I seeing this?"** → trigger + exact data used
   + "guidance, not a sale."
3. **Idle Saver (Flow A).** ₹47k idle 152+ days → Sweep-FD nudge (shown in हिंदी;
   toggle EN; tap 🔊 to hear it).
4. **New Earner (Flow C).** Two moments detected → the agent **suppresses
   `salary_jump`** and surfaces the contextual travel micro-cover (visible in the
   decision log).
5. **The learn loop.** Skip a nudge → reselect the persona → the agent now
   **suppresses** that category (feedback → suitability rule 6).
6. **The reframe.** This moves the sale from a coercive human channel to a
   transparent, consented, suitability-filtered digital one — lifting adoption
   while removing the mis-selling risk SBI is under pressure to fix.
