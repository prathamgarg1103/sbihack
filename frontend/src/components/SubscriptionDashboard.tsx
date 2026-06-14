import { useState } from 'react'
import type { AgentDecision, Subscription } from '../lib/api'

type Lang = 'en' | 'hi'

function rupee(n: number): string {
  return Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })
}

function SubRow({ s, lang }: { s: Subscription; lang: Lang }) {
  const [paused, setPaused] = useState(false)
  const unused = !s.used_last_30d
  return (
    <div className={`rounded-2xl border px-3 py-2.5 ${unused ? 'border-amber-200 bg-amber-50' : 'border-slate-100 bg-white'}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-yono-ink">{s.name}</p>
          <p className="text-[11px] text-slate-400">
            {s.category} · ₹{rupee(s.amount)}/mo · {s.is_mandate ? 'UPI AutoPay' : s.via}
          </p>
        </div>
        <div className="text-right">
          {unused ? (
            <span className="rounded-full bg-amber-200 px-2 py-0.5 text-[9px] font-bold text-amber-800">
              {lang === 'hi' ? '30 दिन से अप्रयुक्त' : 'unused 30d'}
            </span>
          ) : (
            <span className="rounded-full bg-yono-mint/15 px-2 py-0.5 text-[9px] font-bold text-yono-mint">
              {lang === 'hi' ? 'इस्तेमाल में' : 'in use'}
            </span>
          )}
          <p className="mt-0.5 text-[10px] text-slate-400">
            {lang === 'hi' ? `${s.next_charge_in_days} दिन में रिन्यू` : `renews in ${s.next_charge_in_days}d`}
          </p>
        </div>
      </div>
      {s.is_mandate && unused && (
        <button
          onClick={() => setPaused((p) => !p)}
          className={`mt-2 w-full rounded-lg py-1.5 text-[11px] font-semibold ${
            paused
              ? 'bg-slate-100 text-slate-500'
              : 'border border-yono-blue text-yono-blue hover:bg-yono-blue/5'
          }`}
        >
          {paused
            ? lang === 'hi' ? '✓ मैंडेट रोका गया (मॉक)' : '✓ Mandate paused (mock)'
            : lang === 'hi' ? 'मैंडेट रोकें' : 'Pause mandate'}
        </button>
      )}
    </div>
  )
}

export function SubscriptionDashboard({
  decision,
  lang,
  onClose,
  onRedirect,
}: {
  decision: AgentDecision
  lang: Lang
  onClose: () => void
  onRedirect: () => void
}) {
  const subs = decision.subscriptions ?? []
  const g = decision.goal_redirect
  const t =
    lang === 'hi'
      ? { title: 'आपकी सदस्यताएँ', sub: 'बैंक मैंडेट सीधे देखता है', save: 'संभावित बचत',
          close: 'बंद करें', move: 'लक्ष्य में डालें' }
      : { title: 'Your subscriptions', sub: 'SBI sees the mandate directly', save: 'Potential savings',
          close: 'Close', move: 'Move to goal' }

  return (
    <div className="absolute inset-0 z-40 flex flex-col bg-white">
      <div className="flex items-center gap-2 border-b border-slate-100 px-4 pb-3 pt-4">
        <button onClick={onClose} className="text-slate-400 hover:text-slate-600">←</button>
        <div>
          <h3 className="text-sm font-bold text-yono-ink">{t.title}</h3>
          <p className="text-[11px] text-slate-400">{t.sub}</p>
        </div>
        {decision.potential_savings != null && (
          <div className="ml-auto text-right">
            <p className="text-[9px] font-bold uppercase text-slate-400">{t.save}</p>
            <p className="text-sm font-bold text-yono-mint">₹{rupee(decision.potential_savings)}/mo</p>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-3">
        <div className="space-y-2">
          {subs.map((s) => (
            <SubRow key={s.sub_id} s={s} lang={lang} />
          ))}
        </div>

        {/* Goal redirect card */}
        {g && (
          <div className="mt-4 rounded-2xl border border-yono-blue/30 bg-yono-blue/5 p-4">
            <p className="text-sm font-semibold text-yono-ink">{g.text[lang]}</p>
            <div className="mt-3">
              <div className="flex justify-between text-[10px] text-slate-400">
                <span>{g.label}</span>
                <span>₹{rupee(g.saved_after)} / ₹{rupee(g.target)}</span>
              </div>
              <div className="relative mt-1 h-2 overflow-hidden rounded-full bg-slate-200">
                <div className="absolute inset-y-0 left-0 bg-yono-mint" style={{ width: `${g.pct_after}%` }} />
                <div className="absolute inset-y-0 left-0 bg-slate-400" style={{ width: `${g.pct_before}%` }} />
              </div>
              <p className="mt-1 text-right text-[10px] font-semibold text-yono-mint">
                {g.pct_before}% → {g.pct_after}%
              </p>
            </div>
            <button
              onClick={onRedirect}
              className="mt-3 w-full rounded-xl bg-yono-blue py-2.5 text-sm font-semibold text-white hover:bg-yono-blue/90"
            >
              {t.move} · ₹{rupee(g.amount)}
            </button>
          </div>
        )}
      </div>

      <div className="border-t border-slate-100 p-3">
        <button onClick={onClose} className="w-full rounded-xl py-2 text-[12px] font-medium text-slate-400 hover:text-slate-600">
          {t.close}
        </button>
      </div>
    </div>
  )
}
