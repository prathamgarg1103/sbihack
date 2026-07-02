import { useState } from 'react'
import type { ExitAnalysis } from '../lib/api'

type Lang = 'en' | 'hi'

function rupee(n: number): string {
  return Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })
}

/** Reverse mis-selling: the honest exit-cost-vs-stay review for a flagged ULIP.
 *  Every number comes from the fact-sheet corpus doc — including where STAYING wins. */
export function ExitOptionsCard({
  analysis,
  lang,
  onKeep,
  onEscalate,
  onBack,
}: {
  analysis: ExitAnalysis
  lang: Lang
  onKeep: () => void
  onEscalate?: () => void
  onBack: () => void
}) {
  const [escalated, setEscalated] = useState(false)
  const a = analysis
  const t =
    lang === 'hi'
      ? {
          title: 'ईमानदार एग्ज़िट समीक्षा',
          flagged: 'हमने अपनी ही बिक्री को चिह्नित किया',
          paid: 'अब तक भरा', months: 'महीने',
          freeLook: 'फ्री-लुक स्थिति',
          exitNow: 'अभी बाहर निकलें', stay: 'बने रहें (कुछ न करें)',
          stayWins: 'जहाँ बने रहना जीतता है',
          human: 'पहले सलाहकार से बात करें', keep: 'पॉलिसी रखें',
          escalatedTitle: 'एक SBI सलाहकार आपसे संपर्क करेंगे।',
          escalatedBody: 'मार्गदर्शन, बिक्री नहीं — कोई दबाव नहीं।',
          backHome: 'YONO पर वापस', grounded: 'आधार',
        }
      : {
          title: 'Honest exit review',
          flagged: 'we flagged our own sale',
          paid: 'Paid so far', months: 'months',
          freeLook: 'Free-look status',
          exitNow: 'Exit now', stay: 'Stay (do nothing)',
          stayWins: 'Where staying wins',
          human: 'Talk to a human advisor first', keep: 'Keep policy',
          escalatedTitle: 'An SBI advisor will reach out.',
          escalatedBody: 'Guidance, not a sale — no pressure.',
          backHome: 'Back to YONO', grounded: 'Grounded in',
        }

  return (
    <div className="absolute inset-0 z-40 flex flex-col bg-white">
      {/* Header — distinct rose framing: the bank is flagging its own sale */}
      <div className="flex items-center gap-2 border-b border-rose-100 bg-rose-50 px-4 pb-3 pt-4">
        <button onClick={onBack} className="text-slate-400 hover:text-slate-600" aria-label="Back">
          ←
        </button>
        <div>
          <h3 className="text-sm font-bold text-yono-ink">{t.title}</h3>
          <p className="text-[11px] text-rose-600">
            {a.product} · {t.flagged}
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-3">
        {/* Summary chips */}
        <div className="mt-2 flex flex-wrap gap-1.5">
          <span className="rounded-lg bg-yono-paper px-2 py-1 text-[11px] font-medium text-yono-ink">
            ₹{rupee(a.monthly_premium)}/mo
          </span>
          <span className="rounded-lg bg-yono-paper px-2 py-1 text-[11px] font-medium text-yono-ink">
            {t.paid}: ₹{rupee(a.paid_so_far)} · {a.months_paid} {t.months}
          </span>
        </div>

        {/* Free-look status */}
        <div
          className={`mt-3 rounded-xl border px-3 py-2 ${
            a.free_look.within_window
              ? 'border-yono-mint/40 bg-yono-mint/10'
              : 'border-slate-200 bg-slate-50'
          }`}
        >
          <p className="text-[10px] font-bold uppercase tracking-wide text-slate-400">{t.freeLook}</p>
          <p className="mt-0.5 text-[12px] leading-snug text-slate-700">{a.free_look.note[lang]}</p>
        </div>

        {/* Exit now */}
        <div className="mt-2 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2">
          <p className="text-[10px] font-bold uppercase tracking-wide text-rose-700">{t.exitNow}</p>
          <div className="mt-1 space-y-0.5 text-[12px]">
            <div className="flex justify-between">
              <span className="text-slate-500">{lang === 'hi' ? 'फंड मूल्य (अनुमानित)' : 'Fund value (est.)'}</span>
              <span className="font-medium text-yono-ink">₹{rupee(a.exit_now.fund_value_estimate)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">{lang === 'hi' ? 'सरेंडर चार्ज' : 'Surrender charge'}</span>
              <span className="font-medium text-rose-600">−₹{rupee(a.exit_now.surrender_charge)}</span>
            </div>
            <div className="flex justify-between border-t border-rose-200 pt-0.5">
              <span className="font-semibold text-slate-600">{lang === 'hi' ? 'वापसी (अनुमानित)' : 'You get back (est.)'}</span>
              <span className="font-bold text-yono-ink">₹{rupee(a.exit_now.refund_estimate)}</span>
            </div>
          </div>
          <p className="mt-1.5 text-[11px] leading-snug text-slate-600">{a.exit_now.note[lang]}</p>
        </div>

        {/* Stay — the do-nothing baseline, with the rows where it genuinely wins */}
        <div className="mt-2 rounded-xl border border-slate-200 bg-white px-3 py-2">
          <p className="text-[10px] font-bold uppercase tracking-wide text-slate-400">{t.stay}</p>
          <p className="mt-0.5 text-[12px] leading-snug text-slate-700">{a.stay.note[lang]}</p>
          <p className="mt-1.5 text-[10px] font-bold uppercase tracking-wide text-amber-700">{t.stayWins}</p>
          <ul className="mt-0.5 space-y-0.5">
            {a.stay.wins.map((w) => (
              <li key={w} className="text-[11px] text-amber-900">
                ✓ {w}
              </li>
            ))}
          </ul>
        </div>

        {/* Sources */}
        <div className="mt-3">
          <p className="text-[10px] font-bold uppercase tracking-wide text-slate-400">{t.grounded}</p>
          <div className="mt-1 flex flex-wrap gap-1">
            {a.sources.map((s) => (
              <span key={s} className="rounded bg-yono-paper px-1.5 py-0.5 text-[10px] text-slate-500">
                {s}
              </span>
            ))}
          </div>
        </div>
        <p className="mt-2 text-[10px] italic text-slate-400">{a.disclaimer}</p>
      </div>

      {/* Actions — human first; keeping the policy is always fine */}
      <div className="border-t border-slate-100 p-3">
        {escalated ? (
          <div className="rounded-xl border border-yono-mint/30 bg-yono-mint/10 px-3 py-2.5 text-center">
            <p className="text-[12px] font-semibold text-yono-ink">{t.escalatedTitle}</p>
            <p className="mt-0.5 text-[11px] text-slate-500">{t.escalatedBody}</p>
            <button onClick={onBack} className="mt-2 text-[12px] font-medium text-yono-blue hover:underline">
              {t.backHome}
            </button>
          </div>
        ) : (
          <>
            <button
              onClick={() => {
                onEscalate?.()
                setEscalated(true)
              }}
              className="w-full rounded-xl border border-yono-blue py-2.5 text-sm font-semibold text-yono-blue hover:bg-yono-blue/5"
            >
              {t.human}
            </button>
            <button
              onClick={onKeep}
              className="mt-2 w-full rounded-xl py-2 text-[12px] font-medium text-slate-400 hover:text-slate-600"
            >
              {t.keep}
            </button>
          </>
        )}
      </div>
    </div>
  )
}
