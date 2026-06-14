import { useState } from 'react'
import type { Walkthrough } from '../lib/api'

type Lang = 'en' | 'hi'

const STEP_ICON = ['📄', '⚡', '🏢', '✅']

export function CoachmarkWalkthrough({
  walkthrough,
  lang,
  onAdopt,
  onClose,
}: {
  walkthrough: Walkthrough
  lang: Lang
  onAdopt: () => void
  onClose: () => void
}) {
  const steps = walkthrough.steps
  const [i, setI] = useState(0)
  const [done, setDone] = useState(false)
  const last = i === steps.length - 1

  const t =
    lang === 'hi'
      ? { guide: 'मार्गदर्शन', next: 'आगे', pay: 'भुगतान करें', step: 'चरण', of: 'में से',
          tap: 'यहाँ टैप करें', back: 'बंद करें',
          doneTitle: 'हो गया! बिल YONO में भर गया', doneBody: 'अब अगली बार यह 30 सेकंड में हो जाएगा।',
          unlocked: 'अनलॉक हुआ' }
      : { guide: 'Guided walkthrough', next: 'Next', pay: 'Complete payment', step: 'Step', of: 'of',
          tap: 'Tap here', back: 'Close',
          doneTitle: 'Done! Bill paid inside YONO', doneBody: 'Next time this takes you 30 seconds.',
          unlocked: 'Unlocked' }

  if (done) {
    return (
      <div className="absolute inset-0 z-40 flex flex-col items-center justify-center bg-white px-6 text-center">
        <div className="grid h-16 w-16 place-items-center rounded-full bg-yono-mint/15 text-3xl">✅</div>
        <h3 className="mt-4 text-lg font-bold text-yono-ink">{t.doneTitle}</h3>
        <p className="mt-1 text-sm text-slate-500">{t.doneBody}</p>
        <div className="mt-4 rounded-xl bg-yono-blue/5 px-4 py-2 text-sm">
          <span className="text-[10px] font-bold uppercase tracking-wide text-yono-blue">
            {t.unlocked}
          </span>
          <p className="font-semibold text-yono-ink">AutoPay →</p>
        </div>
        <button
          onClick={onAdopt}
          className="mt-6 w-full rounded-xl bg-yono-blue py-2.5 text-sm font-semibold text-white hover:bg-yono-blue/90"
        >
          {lang === 'hi' ? 'बढ़िया' : 'Great'}
        </button>
      </div>
    )
  }

  return (
    <div className="absolute inset-0 z-40 flex flex-col bg-white">
      {/* Mock Bill-Pay app header */}
      <div className="flex items-center gap-2 bg-gradient-to-r from-yono-blue to-yono-sky px-4 pb-3 pt-5 text-white">
        <button onClick={onClose} className="text-white/80 hover:text-white" aria-label={t.back}>
          ←
        </button>
        <div>
          <p className="text-[11px] opacity-80">YONO · {walkthrough.display}</p>
          <p className="text-sm font-semibold">
            {t.step} {i + 1} {t.of} {steps.length}
          </p>
        </div>
        <span className="ml-auto rounded-full bg-white/20 px-2 py-0.5 text-[10px] font-bold">
          {t.guide}
        </span>
      </div>

      {/* Progress */}
      <div className="flex gap-1 px-4 pt-3">
        {steps.map((_, k) => (
          <div
            key={k}
            className={`h-1 flex-1 rounded-full ${k <= i ? 'bg-yono-mint' : 'bg-slate-200'}`}
          />
        ))}
      </div>

      {/* Mock screen with the step rows */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <div className="space-y-2">
          {steps.map((s, k) => {
            const active = k === i
            const complete = k < i
            return (
              <div key={s} className="relative">
                <div
                  className={`flex items-center gap-3 rounded-2xl border px-3 py-3 transition ${
                    active
                      ? 'border-yono-blue bg-yono-blue/5 shadow-md ring-2 ring-yono-blue'
                      : complete
                        ? 'border-slate-100 bg-slate-50 opacity-60'
                        : 'border-slate-100 bg-white opacity-50'
                  }`}
                >
                  <div className="grid h-9 w-9 place-items-center rounded-xl bg-yono-paper text-lg">
                    {complete ? '✓' : STEP_ICON[k] ?? '•'}
                  </div>
                  <span className={`text-sm ${active ? 'font-semibold text-yono-ink' : 'text-slate-500'}`}>
                    {s}
                  </span>
                </div>
                {active && (
                  <div className="absolute -right-1 -top-2 z-10 animate-pulse rounded-lg bg-yono-ink px-2 py-1 text-[10px] font-bold text-white shadow-lg">
                    {t.tap}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Advance */}
      <div className="border-t border-slate-100 p-3">
        <button
          onClick={() => (last ? setDone(true) : setI((v) => v + 1))}
          className="w-full rounded-xl bg-yono-blue py-2.5 text-sm font-semibold text-white hover:bg-yono-blue/90"
        >
          {last ? t.pay : t.next}
        </button>
      </div>
    </div>
  )
}
