import { useState } from 'react'
import type { AgentDecision, Moment } from '../lib/api'

type Lang = 'en' | 'hi'

function rupee(n: number): string {
  return Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })
}

/** 1–3 human-readable evidence chips from the surfaced moment. */
function chips(m: Moment): string[] {
  const e = m.evidence
  switch (m.trigger_type) {
    case 'premium_leak':
      return [`₹${rupee(e.monthly_premium as number)}/mo`, `₹${rupee(e.annual_premium as number)}/yr`, `${e.occurrences} payments`]
    case 'idle_balance':
      return [`₹${rupee(e.idle_amount as number)} idle`, `${e.days_idle}+ days`, `${e.savings_rate_pct}% p.a.`]
    case 'salary_jump':
      return [`₹${rupee(e.previous_salary as number)} → ₹${rupee(e.latest_salary as number)}`, `+${e.increase_pct}%`]
    case 'contextual_spend':
      return [`₹${rupee(e.amount as number)}`, String(e.spend_kind), String(e.cover_type)]
    default:
      return []
  }
}

function dataUsed(m: Moment): [string, string][] {
  return Object.entries(m.evidence).map(([k, v]) => [
    k.replace(/_/g, ' '),
    typeof v === 'number' && /amount|premium|salary/.test(k) ? `₹${rupee(v)}` : String(v),
  ])
}

function speak(text: string, lang: Lang) {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = lang === 'hi' ? 'hi-IN' : 'en-IN'
  window.speechSynthesis.speak(u)
}

export function NudgeCard({
  decision,
  lang,
  onLang,
  onSkip,
  onPrimary,
}: {
  decision: AgentDecision
  lang: Lang
  onLang: (l: Lang) => void
  onSkip: () => void
  onPrimary: () => void
}) {
  const [why, setWhy] = useState(false)
  const moment = decision.surfaced_moment
  const nudge = decision.nudge
  if (!moment || !nudge) return null

  return (
    <div className="absolute inset-x-0 bottom-0 z-30 px-3 pb-3">
      <div className="rounded-3xl bg-white p-4 shadow-[0_-8px_40px_rgba(11,31,58,0.25)] ring-1 ring-slate-200">
        {/* Agent header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="grid h-7 w-7 place-items-center rounded-full bg-gradient-to-br from-yono-blue to-yono-mint text-xs font-bold text-white">
              ✦
            </div>
            <span className="text-sm font-semibold text-yono-ink">Saarthi</span>
            <span className="rounded-full bg-yono-mint/15 px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide text-yono-mint">
              guidance · not a sale
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            {/* Voice */}
            <button
              onClick={() => speak(`${nudge.title[lang]}. ${nudge.body[lang]}`, lang)}
              className="grid h-6 w-6 place-items-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-yono-blue"
              aria-label="Read aloud"
              title="Read aloud"
            >
              🔊
            </button>
            {/* EN / HI toggle */}
            <div className="flex overflow-hidden rounded-full border border-slate-200 text-[10px] font-bold">
              {(['en', 'hi'] as Lang[]).map((l) => (
                <button
                  key={l}
                  onClick={() => onLang(l)}
                  className={`px-2 py-0.5 ${lang === l ? 'bg-yono-blue text-white' : 'text-slate-500'}`}
                >
                  {l === 'en' ? 'EN' : 'हिं'}
                </button>
              ))}
            </div>
            <button onClick={onSkip} className="text-slate-300 hover:text-slate-500" aria-label="Skip">
              ✕
            </button>
          </div>
        </div>

        {/* Body (agent-written, bilingual) */}
        <h3 className="mt-3 text-[15px] font-bold leading-snug text-yono-ink">{nudge.title[lang]}</h3>
        <p className="mt-1 text-[13px] leading-relaxed text-slate-600">{nudge.body[lang]}</p>

        <div className="mt-2.5 flex flex-wrap gap-1.5">
          {chips(moment).map((c) => (
            <span key={c} className="rounded-lg bg-yono-paper px-2 py-1 text-[11px] font-medium text-yono-ink">
              {c}
            </span>
          ))}
        </div>

        {/* Explainability reveal */}
        <button
          onClick={() => setWhy((v) => !v)}
          className="mt-3 text-[11px] font-semibold text-yono-blue underline decoration-dotted underline-offset-2"
        >
          {why ? 'Hide' : 'Why am I seeing this?'}
        </button>
        {why && (
          <div className="mt-2 rounded-xl border border-slate-200 bg-yono-paper/60 p-3">
            <p className="text-[10px] font-bold uppercase tracking-wide text-slate-400">Trigger</p>
            <p className="text-[12px] text-yono-ink">
              {moment.trigger_type.replace(/_/g, ' ')} · detected from your own transactions
            </p>
            <p className="mt-2 text-[10px] font-bold uppercase tracking-wide text-slate-400">Data used</p>
            <dl className="mt-0.5 space-y-0.5">
              {dataUsed(moment).map(([k, v]) => (
                <div key={k} className="flex justify-between gap-3 text-[12px]">
                  <dt className="capitalize text-slate-500">{k}</dt>
                  <dd className="text-right font-medium text-yono-ink">{v}</dd>
                </div>
              ))}
            </dl>
            <p className="mt-2 text-[11px] italic text-slate-500">
              This is guidance, not a sale. No data leaves your account without consent.
            </p>
          </div>
        )}

        {/* Actions */}
        <button
          onClick={onPrimary}
          className="mt-3 w-full rounded-xl bg-yono-blue py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-yono-blue/90"
        >
          {nudge.cta[lang]}
        </button>
        <div className="mt-2 flex gap-2">
          <button className="flex-1 rounded-xl border border-slate-200 py-2 text-[12px] font-medium text-slate-600 hover:border-slate-300">
            {lang === 'hi' ? 'सलाहकार से बात करें' : 'Talk to a human advisor'}
          </button>
          <button onClick={onSkip} className="rounded-xl px-4 py-2 text-[12px] font-medium text-slate-400 hover:text-slate-600">
            {lang === 'hi' ? 'छोड़ें' : 'Skip'}
          </button>
        </div>
      </div>
    </div>
  )
}
