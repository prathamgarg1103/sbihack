import type { AttentionBudget } from '../lib/api'

/** Always-visible attention-budget meter: Diya may interrupt each user at most
 *  4 times per month — restraint made visible, not just claimed. */
export function AttentionMeter({
  budget,
  lang,
}: {
  budget?: AttentionBudget | null
  lang: 'en' | 'hi'
}) {
  if (!budget) return null
  const exhausted = budget.remaining === 0
  return (
    <div
      className={`flex items-center gap-2.5 rounded-full border bg-white px-3.5 py-1.5 text-[11px] shadow-sm ${
        exhausted ? 'border-yono-amber/50' : 'border-slate-200'
      }`}
    >
      <span className="font-bold uppercase tracking-wide text-slate-400">
        {lang === 'hi' ? 'ध्यान बजट' : 'Attention budget'}
      </span>
      <div className="flex gap-1">
        {Array.from({ length: budget.cap }, (_, i) => (
          <span
            key={i}
            className={`h-2 w-2 rounded-full ${
              i < budget.used ? (exhausted ? 'bg-yono-amber' : 'bg-yono-blue') : 'bg-slate-200'
            }`}
          />
        ))}
      </div>
      <span className={exhausted ? 'font-semibold text-yono-amber' : 'text-slate-500'}>
        {lang === 'hi'
          ? `Diya ने इस महीने ${budget.cap} में से ${budget.used} रुकावटें इस्तेमाल कीं`
          : `Diya has used ${budget.used} of ${budget.cap} interruptions this month`}
      </span>
    </div>
  )
}
