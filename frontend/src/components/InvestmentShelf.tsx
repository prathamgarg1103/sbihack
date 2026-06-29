import { useState } from 'react'
import type { AgentDecision, Fund, Stock } from '../lib/api'

type Lang = 'en' | 'hi'

function AmcBadge({ isSbi, amc }: { isSbi: boolean; amc: string }) {
  return (
    <span
      className={`rounded px-1.5 py-0.5 text-[9px] font-bold ${
        isSbi ? 'bg-yono-blue/10 text-yono-blue' : 'bg-slate-100 text-slate-500'
      }`}
    >
      {amc}
    </span>
  )
}

function FundRow({ f, cheapest, topReturn }: { f: Fund; cheapest: boolean; topReturn: boolean }) {
  return (
    <div className="flex items-center gap-2 border-b border-slate-100 px-1 py-2 last:border-0">
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1.5">
          <p className="truncate text-[12px] font-semibold text-yono-ink">{f.name}</p>
          <AmcBadge isSbi={f.is_sbi} amc={f.amc} />
        </div>
        <p className="text-[10px] text-slate-400">{f.category}</p>
      </div>
      <div className="text-right">
        <p className={`text-[12px] font-semibold ${topReturn ? 'text-yono-mint' : 'text-slate-600'}`}>
          {f.return_5y}%
        </p>
        <p className="text-[9px] text-slate-400">5y · illus.</p>
      </div>
      <div className="w-14 text-right">
        <p className={`text-[12px] ${cheapest ? 'font-bold text-yono-mint' : 'text-slate-500'}`}>
          {f.expense_ratio}%
        </p>
        <p className="text-[9px] text-slate-400">cost</p>
      </div>
    </div>
  )
}

function StockChip({ s }: { s: Stock }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-100 bg-white px-2.5 py-1.5">
      <div>
        <div className="flex items-center gap-1.5">
          <p className="text-[12px] font-bold text-yono-ink">{s.symbol}</p>
          {s.is_sbi && <AmcBadge isSbi amc="SBI" />}
        </div>
        <p className="text-[10px] text-slate-400">{s.name}</p>
      </div>
      <span className="text-[10px] text-slate-400">{s.sector}</span>
    </div>
  )
}

export function InvestmentShelf({
  decision,
  lang,
  onClose,
  onInvest,
  onEscalate,
}: {
  decision: AgentDecision
  lang: Lang
  onClose: () => void
  onInvest: () => void
  onEscalate?: () => void
}) {
  const [escalated, setEscalated] = useState(false)
  const shelf = decision.investment_shelf
  if (!shelf) return null

  // Honesty cues: cheapest index fund + highest illustrative return (often non-SBI).
  const minExpense = Math.min(...shelf.funds.map((f) => f.expense_ratio))
  const maxReturn = Math.max(...shelf.funds.map((f) => f.return_5y))

  return (
    <div className="absolute inset-0 z-40 flex flex-col bg-white">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-slate-100 px-4 pb-3 pt-4">
        <button onClick={onClose} className="text-slate-400 hover:text-slate-600" aria-label="Back">
          ←
        </button>
        <div>
          <h3 className="text-sm font-bold text-yono-ink">
            {lang === 'hi' ? 'मार्केट — पूरा बाज़ार' : 'Markets — the whole shelf'}
          </h3>
          <p className="text-[11px] text-slate-400">
            {lang === 'hi' ? 'SBI के फंड्स और बाकी सबके भी' : "SBI's funds and everyone else's"}
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-3">
        {/* Neutrality banner — the open-shelf thesis, up front */}
        <div className="mt-2 rounded-xl border border-yono-blue/20 bg-yono-blue/5 px-3 py-2">
          <div className="mb-1 flex flex-wrap gap-1">
            <span className="rounded-full bg-white px-1.5 py-0.5 text-[9px] font-bold text-yono-blue">
              {shelf.fund_count} funds
            </span>
            <span className="rounded-full bg-white px-1.5 py-0.5 text-[9px] font-semibold text-slate-500">
              {shelf.sbi_fund_count} SBI · {shelf.other_fund_count} others
            </span>
            <span className="rounded-full bg-white px-1.5 py-0.5 text-[9px] font-semibold text-slate-500">
              {shelf.stock_count} stocks
            </span>
          </div>
          <p className="text-[11px] leading-snug text-slate-600">⚖️ {shelf.neutrality_note}</p>
        </div>

        {/* The honesty proof — Diya points to a non-SBI winner */}
        {shelf.honest_highlight && (
          <div className="mt-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2">
            <p className="text-[10px] font-bold uppercase text-amber-800">
              {lang === 'hi' ? 'जहाँ कोई और बेहतर है' : 'Where a non-SBI option wins'}
            </p>
            <p className="text-[12px] leading-snug text-amber-900">{shelf.honest_highlight}</p>
          </div>
        )}

        {/* Mutual funds */}
        <div className="mt-3">
          <p className="px-1 text-[10px] font-bold uppercase tracking-wide text-slate-400">
            {lang === 'hi' ? 'म्यूचुअल फंड्स' : 'Mutual funds'}
          </p>
          <div className="mt-1 rounded-xl border border-slate-100">
            {shelf.funds.map((f) => (
              <FundRow
                key={f.name}
                f={f}
                cheapest={f.expense_ratio === minExpense}
                topReturn={f.return_5y === maxReturn}
              />
            ))}
          </div>
        </div>

        {/* Stocks */}
        <div className="mt-3">
          <p className="px-1 text-[10px] font-bold uppercase tracking-wide text-slate-400">
            {lang === 'hi' ? 'स्टॉक्स (ट्रेड के लिए उपलब्ध)' : 'Stocks (available to trade)'}
          </p>
          <div className="mt-1 grid grid-cols-1 gap-1.5">
            {shelf.stocks.map((s) => (
              <StockChip key={s.symbol} s={s} />
            ))}
          </div>
          <p className="mt-1 text-[9px] italic text-slate-400">
            {lang === 'hi'
              ? 'डेमो — लाइव भाव नहीं दिखाए गए। बात इतनी है कि गैर-SBI स्टॉक भी सूचीबद्ध हैं।'
              : 'Demo — live prices not shown. The point: non-SBI stocks are listed too.'}
          </p>
        </div>

        {/* Suitability + sources + disclaimer */}
        <div className="mt-3 rounded-xl bg-yono-mint/10 px-3 py-2">
          <p className="text-[11px] text-slate-700">
            ✓ {lang === 'hi'
              ? 'इंडेक्स फंड और SIP साधारण, गैर-ULIP हैं — Diya के फ़िल्टर से पास।'
              : 'Index funds & SIPs are simple, non-ULIP — they pass Diya’s filter.'}
          </p>
        </div>
        <div className="mt-3">
          <p className="text-[10px] font-bold uppercase tracking-wide text-slate-400">Grounded in</p>
          <div className="mt-1 flex flex-wrap gap-1">
            {shelf.sources.map((s) => (
              <span key={s} className="rounded bg-yono-paper px-1.5 py-0.5 text-[10px] text-slate-500">
                {s}
              </span>
            ))}
          </div>
        </div>
        <p className="mt-2 text-[10px] italic text-slate-400">{shelf.disclaimer}</p>
      </div>

      {/* Actions */}
      <div className="border-t border-slate-100 p-3">
        {escalated ? (
          <div className="rounded-xl border border-yono-mint/30 bg-yono-mint/10 px-3 py-2.5 text-center">
            <p className="text-[12px] font-semibold text-yono-ink">
              {lang === 'hi' ? 'एक SBI सलाहकार आपको निवेश में मदद करेंगे।' : 'An SBI advisor will help you invest.'}
            </p>
            <p className="mt-0.5 text-[11px] text-slate-500">
              {lang === 'hi' ? 'मार्गदर्शन, बिक्री नहीं।' : 'Guidance, not a sale.'}
            </p>
            <button onClick={onClose} className="mt-2 text-[12px] font-medium text-yono-blue hover:underline">
              {lang === 'hi' ? 'YONO पर वापस' : 'Back to YONO'}
            </button>
          </div>
        ) : (
          <>
            <button
              onClick={onInvest}
              className="w-full rounded-xl bg-yono-blue py-2.5 text-sm font-semibold text-white hover:bg-yono-blue/90"
            >
              {lang === 'hi' ? 'एक SIP शुरू करें' : 'Start a SIP'}
            </button>
            <div className="mt-2 flex gap-2">
              <button
                onClick={() => {
                  onEscalate?.()
                  setEscalated(true)
                }}
                className="flex-1 rounded-xl border border-slate-200 py-2 text-[12px] font-medium text-slate-600 hover:border-slate-300"
              >
                {lang === 'hi' ? 'सलाहकार से बात करें' : 'Talk to a human advisor'}
              </button>
              <button onClick={onClose} className="rounded-xl px-4 py-2 text-[12px] font-medium text-slate-400 hover:text-slate-600">
                {lang === 'hi' ? 'अभी नहीं' : 'Not now'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
