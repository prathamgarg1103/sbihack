# Diya — Shot List (capture checklist)

> Record these once the six new features land. One clip per shot, named exactly as listed, saved
> to `video/footage/`. Every clip should start **3–5 s before** the first click and end **3–5 s
> after** the last visual settles ("handles" for the edit). Scene timings and narration are in
> `video/FINAL_VIDEO_SCRIPT.md`.

---

## Recording settings (do this first)

- **Resolution:** capture at 1920×1080 (or capture 2560×1440 and downscale — crisper text).
  Set Windows display scaling to 100% for the recording session if the app allows it.
- **Frame rate:** 60 fps if your recorder supports it, else 30 fps. (OBS Studio: Settings →
  Video → 60; Xbox Game Bar: Settings → Captures → 60 fps.)
- **Cursor:** enable cursor highlighting / click visualization (OBS: add a "highlight cursor"
  plugin, or use PowerToys Mouse Highlighter — Win+Shift+H). Judges follow the cursor.
- **Browser:** Chrome/Edge, zoom **100–110%** (110% recommended — matches prior recordings),
  bookmarks bar hidden (Ctrl+Shift+B), a clean profile/window, no extensions visible, no other
  tabs. F11 full-screen or crop the chrome in the edit.
- **System hygiene:** Focus Assist / Do Not Disturb ON, notifications off, close Slack/Discord,
  hide desktop icons if the desktop is ever visible.
- **App state:** backend running (`.venv\Scripts\python -m uvicorn main:app --port 8000` from
  `/backend`), frontend `npm run dev` → `http://localhost:5173`. Put `ANTHROPIC_API_KEY` in the
  repo-root `.env` so the Agent Decision Loop badge reads **LLM live** (rules-mode looks fine
  but be consistent across ALL shots — don't mix badges).
- **Clean slate before shooting:** click **reset** in each persona's decision panel (clears
  learned feedback), and reset the attention-budget counter to the state you want on camera
  (2 of 4 used — pre-trigger two nudges on a throwaway persona if the counter is global).
- Record each shot in its own take. Re-record until the clicks are smooth — no hunting.

---

## Shot 1 — `shot01_problem.mp4` (for Scene 1, need ≥ 26 s usable)

- **Setup:** Demo tab, any persona pre-selected but no nudge open. Agent Decision Loop panel
  visible with **LLM live** badge.
- **Action:** no clicks. Slow cursor drift over the phone shell; at ~12 s glide to the decision
  panel and rest on the badge.
- **Expected visual:** calm hero shot of the app + visible proof the agent is live.

## Shot 2 — `shot02_flowb_consent.mp4` (Scene 2, first half)

- **Setup:** Demo tab, no persona active (or freshly reset).
- **Action:** click **Premium Leaker (Rahul)** → consent gate slides up in Hindi → pause 2 s →
  click **हाँ, विश्लेषण करें** → Hindi nudge appears (₹1,240/mo to competitor insurer). Hold 3 s.
- **Expected visual:** Hindi consent gate, then Hindi nudge card with the leak amount.

## Shot 3 — `shot03_flowb_comparison.mp4` (Scene 2, second half)

- **Setup:** continue from Shot 2 state (nudge visible).
- **Action:** click the primary CTA → honest comparison opens. Cursor: rest 2 s on the amber
  **competitor-wins row** (claim-settlement ratio) → 2 s on the **"Do nothing" column** → 2 s on
  **"Talk to a human advisor"**. No clicks after the CTA.
- **Expected visual:** full comparison table with all three elements clearly on screen at once.
- **Checklist:** [ ] competitor-wins row visible [ ] Do-nothing column visible [ ] human-advisor
  button visible [ ] no scrolling needed mid-shot (resize/zoom so the table fits).

## Shot 4 — `shot04_reverse_misselling.mp4` (Scene 3, need ≥ 22 s usable — the jaw-drop)

- **Setup:** Rahul persona with the reverse mis-selling flag triggered (he owns a synthetic ULIP).
- **Action:** the flag card appears (or scroll to it) → pause 2 s → click it → **Exit vs Stay**
  view opens → cursor rests 2–3 s on the surrender-charges figure → 2–3 s on the Stay column →
  hold the full split view 3 s.
- **Expected visual:** "unsuitable product you already own" flag, then both sides of the honest
  exit-vs-stay math. This is the money shot — reshoot until it's perfect.

## Shot 5 — `shot05_xai_devils_advocate.mp4` (Scene 4)

- **Setup:** Rahul's nudge visible again (back out of the comparison).
- **Action:** click **"Why am I seeing this?"** → XAI card opens → scroll slowly to the
  **Devil's Advocate objections** section → hold 3 s.
- **Expected visual:** trigger + honest math + data-used, then the counter-agent's objections
  printed on the card.

## Shot 6 — `shot06_suppressed_nudge.mp4` (Scene 4, cutaway, need ~5 s)

- **Setup:** a persona/event where the devil's advocate objection was rated STRONG.
- **Action:** show the Agent Decision Loop / decision log with the **SUPPRESSED** decision line
  (objection → suppress). Cursor points at it. No clicks.
- **Expected visual:** log line proving a nudge was killed before the user ever saw it.

## Shot 7 — `shot07_flowa_budget_walkthrough.mp4` (Scene 5)

- **Setup:** fresh state; attention budget showing **2 of 4 used**.
- **Action:** click **Idle Saver** → allow consent → sweep-FD nudge appears → toggle **EN/हिं**
  once → tap **🔊** (let 1–2 s of app TTS play) → cursor rests 2 s on the **attention budget
  meter** → click through the guided walkthrough coachmarks to completion → final "done" state.
- **Expected visual:** nudge in both languages, speaker working, "2 / 4 interruptions" meter
  clearly legible, coachmark walkthrough completing.
- **Checklist:** [ ] meter says 2 of 4 [ ] voice audibly plays [ ] walkthrough completes without
  a mis-click.

## Shot 8 — `shot08_sahayak.mp4` (Scene 6)

- **Setup:** elderly persona (Kamla, 72) with guardian/Sahayak configured (daughter).
- **Action:** Kamla accepts the FD nudge → **"Waiting for Sahayak approval"** pending state
  (hold 2 s) → switch to the guardian view (second panel/simulated second device) → the request
  with the same honest math → click **Approve** → back on Kamla's screen: confirmed.
- **Expected visual:** the blocked-until-co-approved state, the guardian's screen, and the
  confirmation. If the guardian view is a separate browser window, record both windows side by
  side or capture the switch cleanly.

## Shot 9 — `shot09_compliance.mp4` (Scene 7)

- **Setup:** several decisions already logged this session (shoot this shot LAST so the trail is
  full — including the suppression from Shot 6 and the co-approval from Shot 8).
- **Action:** click **Mission Control** → open the **Compliance** tab → hash-chained log visible
  → click one entry → expanded decision replay (trigger, tools, objections, outcome) → if the
  tamper-demo exists, toggle it 1 s to show the chain breaking, toggle back.
- **Expected visual:** hashes visibly chaining row to row; one entry fully expanded.

## Shot 10 — `shot10_mission_control_hold.mp4` (Scene 8, need ≥ 24 s usable)

- **Setup:** Mission Control main view, decisions streaming across all personas.
- **Action:** no clicks; let it run. Slow cursor drift or none at all.
- **Expected visual:** the agent autonomously deciding per user: nudge / hold / stay silent.

## Shot 11 — b-roll trio for Scene 9 (~4 s usable each)

- `shot11a_open_shelf.mp4` — New Earner → **Markets, the whole shelf** screen; cursor on the
  non-SBI winners (cheaper index fund, flexi-cap).
- `shot11b_flowd_walkthrough.mp4` — Explorer → Bill-Pay discovery card → 2–3 coachmark steps.
- `shot11c_mission_control.mp4` — 3 s of the Mission Control grid (can reuse Shot 10).

## Shot 12 — `shot12_endcard.png` (Scene 9 end card, still image)

- Diya name/logo, live deployment URL + QR code, team name. Export as a 1920×1080 PNG
  (make it in the app, a slide, or Figma — just keep fonts consistent with the deck).

---

## Coverage map (shot → scene)

| Scene | Shots |
|---|---|
| 1 | 1 |
| 2 | 2, 3 |
| 3 | 4 |
| 4 | 5, 6 |
| 5 | 7 |
| 6 | 8 |
| 7 | 9 |
| 8 | 10 |
| 9 | 11a, 11b, 11c, 12 |

**After capture:** drop all clips in `video/footage/`, then follow `video/ASSEMBLY.md`.
