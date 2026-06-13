import { useState } from 'react'
import type { Moment } from '../lib/api'

const CTA: Record<Moment['suggested_category'], string> = {
  fixed_deposit: 'Open a Sweep FD',
  insurance_compare: 'See the honest comparison',
  micro_cover: 'Add optional cover',
}

function rupee(n: number): string {
  return Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })
}

/** Pull 1–3 human-readable evidence chips out of the moment, by trigger type. */
function chips(m: Moment): string[] {
  const e = m.evidence
  switch (m.trigger_type) {
    case 'premium_leak':
      return [
        `₹${rupee(e.monthly_premium as number)}/mo`,
        `₹${rupee(e.annual_premium as number)}/yr`,
        `${e.occurrences} payments`,
      ]
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

/** "Data used" rows for the explainability reveal. */
function dataUsed(m: Moment): [string, string][] {
  return Object.entries(m.evidence).map(([k, v]) => [
    k.replace(/_/g, ' '),
    typeof v === 'number' && /amount|premium|salary/.test(k) ? `₹${rupee(v)}` : String(v),
  ])
}

export function NudgeCard({ moment, onSkip }: { moment: Moment; onSkip: () => void }) {
  const [why, setWhy] = useState(false)

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
          <button onClick={onSkip} className="text-slate-300 hover:text-slate-500" aria-label="Skip">
            ✕
          </button>
        </div>

        {/* Body */}
        <h3 className="mt-3 text-[15px] font-bold leading-snug text-yono-ink">{moment.title}</h3>
        <p className="mt-1 text-[13px] leading-relaxed text-slate-600">{moment.summary}</p>

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
                <div key={k} className="flex justify-between text-[12px]">
                  <dt className="capitalize text-slate-500">{k}</dt>
                  <dd className="font-medium text-yono-ink">{v}</dd>
                </div>
              ))}
            </dl>
            <p className="mt-2 text-[11px] italic text-slate-500">
              This is guidance, not a sale. No data leaves your account without consent.
            </p>
          </div>
        )}

        {/* Actions */}
        <button className="mt-3 w-full rounded-xl bg-yono-blue py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-yono-blue/90">
          {CTA[moment.suggested_category]}
        </button>
        <div className="mt-2 flex gap-2">
          <button className="flex-1 rounded-xl border border-slate-200 py-2 text-[12px] font-medium text-slate-600 hover:border-slate-300">
            Talk to a human advisor
          </button>
          <button onClick={onSkip} className="rounded-xl px-4 py-2 text-[12px] font-medium text-slate-400 hover:text-slate-600">
            Skip
          </button>
        </div>
      </div>
    </div>
  )
}
