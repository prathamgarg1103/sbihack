import { useState } from 'react'
import type { AgentDecision, Subscription } from '../lib/api'

type Lang = 'en' | 'hi'

function rupee(n: number): string {
  return Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })
}

function SubRow({ s, lang, soon }: { s: Subscription; lang: Lang; soon: boolean }) {
  const [paused, setPaused] = useState(false)
  return (
    <div className={`rounded-2xl border px-3 py-2.5 ${soon ? 'border-amber-200 bg-amber-50' : 'border-slate-100 bg-white'}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-yono-ink">{s.name}</p>
          <p className="text-[11px] text-slate-400">
            {s.category} · ₹{rupee(s.amount)}/mo · {s.is_mandate ? 'UPI AutoPay' : s.via}
          </p>
        </div>
        <span
          className={`rounded-full px-2 py-0.5 text-[9px] font-bold ${
            soon ? 'bg-amber-200 text-amber-800' : 'bg-slate-100 text-slate-500'
          }`}
        >
          {lang === 'hi' ? `${s.next_charge_in_days} दिन में रिन्यू` : `renews in ${s.next_charge_in_days}d`}
        </span>
      </div>
      {s.is_mandate && soon && (
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
      {!s.is_mandate && soon && (
        <p className="mt-1.5 text-[10px] text-slate-400">
          {lang === 'hi' ? 'कार्ड पर — ऐप में जाकर रद्द करें' : 'On card — cancel in the app if you wish'}
        </p>
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
  const flaggedId = decision.flagged?.sub_id
  const days = decision.flagged?.next_charge_in_days
  const g = decision.goal_redirect
  const inv = decision.invest
  const t =
    lang === 'hi'
      ? { title: 'आपकी सदस्यताएँ', sub: 'बैंक मैंडेट सीधे देखता है', monthly: 'कुल मासिक',
          close: 'बंद करें', move: 'लक्ष्य में डालें' }
      : { title: 'Your subscriptions', sub: 'SBI sees the mandate directly', monthly: 'Total monthly',
          close: 'Close', move: 'Move to goal' }

  return (
    <div className="absolute inset-0 z-40 flex flex-col bg-white">
      <div className="flex items-center gap-2 border-b border-slate-100 px-4 pb-3 pt-4">
        <button onClick={onClose} className="text-slate-400 hover:text-slate-600">←</button>
        <div>
          <h3 className="text-sm font-bold text-yono-ink">{t.title}</h3>
          <p className="text-[11px] text-slate-400">{t.sub}</p>
        </div>
        {decision.total_monthly != null && (
          <div className="ml-auto text-right">
            <p className="text-[9px] font-bold uppercase text-slate-400">{t.monthly}</p>
            <p className="text-sm font-bold text-yono-ink">₹{rupee(decision.total_monthly)}/mo</p>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-3">
        {/* Gentle renewal reminder — grounded only in the next-charge date */}
        {decision.flagged && days != null && (
          <div className="mb-3 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2">
            <p className="text-[12px] text-amber-900">
              ⏰{' '}
              {lang === 'hi'
                ? `${decision.flagged.name} ${days} दिनों में रिन्यू होगा। अगर इस्तेमाल नहीं कर रहे, तो रोक सकते हैं।`
                : `${decision.flagged.name} renews in ${days} days. If you're not using it, you can pause it.`}
            </p>
          </div>
        )}

        <div className="space-y-2">
          {subs.map((s) => (
            <SubRow key={s.sub_id} s={s} lang={lang} soon={s.sub_id === flaggedId} />
          ))}
        </div>

        {/* Invest-instead — honest, grounded illustration (not a recommendation) */}
        {inv && (
          <div className="mt-4 rounded-2xl border border-yono-mint/30 bg-yono-mint/5 p-4">
            <p className="text-sm font-semibold text-yono-ink">
              {lang === 'hi' ? 'इसे अपने सपने में निवेश करें' : 'Invest it toward your dream instead'}
            </p>
            <p className="text-[11px] text-slate-400">
              {lang === 'hi'
                ? `₹${rupee(inv.monthly)}/माह बचाकर — अनुमानित वृद्धि`
                : `₹${rupee(inv.monthly)}/mo not spent — illustrative growth`}
            </p>
            <div className="mt-2 overflow-hidden rounded-lg border border-slate-100">
              <div className="grid grid-cols-4 bg-slate-50 px-2 py-1 text-[9px] font-bold uppercase text-slate-400">
                <span>{lang === 'hi' ? 'अवधि' : 'In'}</span>
                <span className="text-right">{lang === 'hi' ? 'आप लगाते' : 'You put'}</span>
                <span className="text-right">RD {inv.rd_pct}%</span>
                <span className="text-right">SIP {inv.sip_pct}%*</span>
              </div>
              {inv.scenarios.map((s) => (
                <div key={s.years} className="grid grid-cols-4 border-t border-slate-100 px-2 py-1.5 text-[11px]">
                  <span className="text-slate-500">{s.years}{lang === 'hi' ? ' साल' : 'y'}</span>
                  <span className="text-right text-slate-500">₹{rupee(s.invested)}</span>
                  <span className="text-right text-slate-600">₹{rupee(s.rd_value)}</span>
                  <span className="text-right font-semibold text-yono-mint">₹{rupee(s.sip_value)}</span>
                </div>
              ))}
            </div>
            <p className="mt-1.5 text-[9px] italic leading-snug text-slate-400">* {inv.disclaimer}</p>
          </div>
        )}

        {/* Conditional goal redirect — only if they choose to pause */}
        {g && (
          <div className="mt-4 rounded-2xl border border-yono-blue/30 bg-yono-blue/5 p-4">
            <p className="text-sm font-semibold text-yono-ink">
              {lang === 'hi' ? 'अगर आप इसे रोकते हैं: ' : 'If you pause it: '}
              {g.text[lang]}
            </p>
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
