import { useState } from 'react'
import type { Comparison, ComparisonRow } from '../lib/api'

function cellClass(win: boolean): string {
  return win
    ? 'bg-yono-mint/12 font-semibold text-yono-ink'
    : 'text-slate-500'
}

function Row({ r }: { r: ComparisonRow }) {
  const long = r.dimension === 'Key exclusion'
  return (
    <div className="border-b border-slate-100 last:border-0">
      <p className="px-3 pt-2 text-[10px] font-bold uppercase tracking-wide text-slate-400">
        {r.dimension}
      </p>
      <div className={`grid ${long ? 'grid-cols-1 gap-1' : 'grid-cols-2'} px-1 pb-2`}>
        <div className={`rounded-lg px-2 py-1.5 text-[12px] ${cellClass(r.winner === 'sbi')}`}>
          {r.winner === 'sbi' && <span className="mr-1 text-yono-mint">✓</span>}
          {long && <span className="text-[9px] text-slate-400">SBI Life · </span>}
          {r.sbi}
        </div>
        <div className={`rounded-lg px-2 py-1.5 text-[12px] ${cellClass(r.winner === 'competitor')}`}>
          {r.winner === 'competitor' && <span className="mr-1 text-yono-mint">✓</span>}
          {long && <span className="text-[9px] text-slate-400">Competitor · </span>}
          {r.competitor}
        </div>
      </div>
    </div>
  )
}

export function ComparisonTable({
  data,
  onBack,
  onEscalate,
}: {
  data: Comparison
  onBack: () => void
  onEscalate?: () => void
}) {
  const [escalated, setEscalated] = useState(false)
  return (
    <div className="absolute inset-0 z-40 flex flex-col bg-white">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-slate-100 px-4 pb-3 pt-4">
        <button onClick={onBack} className="text-slate-400 hover:text-slate-600" aria-label="Back">
          ←
        </button>
        <div>
          <h3 className="text-sm font-bold text-yono-ink">Honest comparison</h3>
          <p className="text-[11px] text-slate-400">{data.product_type}</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-3">
        {/* Column headers */}
        <div className="sticky top-0 z-10 grid grid-cols-2 gap-1 bg-white pt-2">
          <div className="rounded-lg bg-yono-blue/5 px-2 py-1.5 text-center">
            <p className="text-[12px] font-bold text-yono-blue">{data.sbi_product.insurer}</p>
            <p className="text-[9px] text-slate-400">yours, if you switch</p>
          </div>
          <div className="rounded-lg bg-slate-100 px-2 py-1.5 text-center">
            <p className="text-[12px] font-bold text-slate-600">{data.competitor_product.insurer}</p>
            <p className="text-[9px] text-slate-400">what you pay now</p>
          </div>
        </div>

        {/* Rows */}
        <div className="mt-2">
          {data.rows.map((r) => (
            <Row key={r.dimension} r={r} />
          ))}
        </div>

        {/* Where the competitor wins — the honesty proof */}
        {data.competitor_wins.length > 0 && (
          <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2">
            <p className="text-[11px] font-bold text-amber-800">
              Where {data.competitor_product.insurer} wins
            </p>
            <p className="text-[12px] text-amber-900">{data.competitor_wins.join(', ')}.</p>
          </div>
        )}

        {/* Savings */}
        {data.annual_saving != null && (
          <div className="mt-2 rounded-xl bg-yono-mint/12 px-3 py-2 text-center">
            <p className="text-[12px] text-slate-600">
              Same cover, you’d save{' '}
              <span className="font-bold text-yono-ink">
                ₹{data.annual_saving.toLocaleString('en-IN')}/year
              </span>
            </p>
          </div>
        )}

        {/* Verdict */}
        <p className="mt-3 text-[12px] leading-relaxed text-slate-700">{data.verdict}</p>

        {/* Sources */}
        <div className="mt-3">
          <p className="text-[10px] font-bold uppercase tracking-wide text-slate-400">
            Grounded in
          </p>
          <div className="mt-1 flex flex-wrap gap-1">
            {data.sources.map((s) => (
              <span key={s} className="rounded bg-yono-paper px-1.5 py-0.5 text-[10px] text-slate-500">
                {s}
              </span>
            ))}
          </div>
        </div>

        <p className="mt-3 text-[10px] italic text-slate-400">{data.disclaimer}</p>
      </div>

      {/* Actions */}
      <div className="border-t border-slate-100 p-3">
        {escalated ? (
          <div className="rounded-xl border border-yono-mint/30 bg-yono-mint/10 px-3 py-2.5 text-center">
            <p className="text-[12px] font-semibold text-yono-ink">
              An SBI advisor will reach out to walk you through both policies.
            </p>
            <p className="mt-0.5 text-[11px] text-slate-500">Guidance, not a sale — no pressure to switch.</p>
            <button
              onClick={onBack}
              className="mt-2 text-[12px] font-medium text-yono-blue hover:underline"
            >
              Back to YONO
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
              Talk to a human advisor first
            </button>
            <button
              onClick={onBack}
              className="mt-2 w-full rounded-xl py-2 text-[12px] font-medium text-slate-400 hover:text-slate-600"
            >
              Not now
            </button>
          </>
        )}
      </div>
    </div>
  )
}
