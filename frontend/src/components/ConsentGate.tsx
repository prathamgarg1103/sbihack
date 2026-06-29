import type { Moment } from '../lib/api'

type Lang = 'en' | 'hi'

const CATEGORY_LABEL: Record<string, { en: string; hi: string }> = {
  premium_leak: { en: 'your insurance payments', hi: 'आपके बीमा भुगतान' },
  idle_balance: { en: 'your savings balance', hi: 'आपकी बचत राशि' },
  contextual_spend: { en: 'your recent spending', hi: 'आपके हाल के खर्च' },
  salary_jump: { en: 'your income', hi: 'आपकी आय' },
}

export function ConsentGate({
  moment,
  lang,
  onAllow,
  onDecline,
}: {
  moment: Moment
  lang: Lang
  onAllow: () => void
  onDecline: () => void
}) {
  const cat = CATEGORY_LABEL[moment.trigger_type] ?? { en: 'this category', hi: 'इस श्रेणी' }
  const t =
    lang === 'hi'
      ? {
          title: 'पहले आपकी अनुमति',
          body: `क्या Diya ${cat.hi} का विश्लेषण कर सकता है ताकि वह सहायक सुझाव दे सके? यह कभी भी बंद किया जा सकता है।`,
          allow: 'हाँ, विश्लेषण करें',
          decline: 'अभी नहीं',
        }
      : {
          title: 'Your permission first',
          body: `May Diya analyse ${cat.en} to offer a helpful, opt-in suggestion? You can revoke this anytime.`,
          allow: 'Yes, analyse',
          decline: 'Not now',
        }

  return (
    <div className="absolute inset-0 z-30 flex items-end bg-yono-ink/30 backdrop-blur-[1px]">
      <div className="m-3 w-full rounded-3xl bg-white p-5 shadow-2xl ring-1 ring-slate-200">
        <div className="flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-yono-blue to-yono-mint text-white">
            🔒
          </div>
          <span className="text-sm font-semibold text-yono-ink">{t.title}</span>
        </div>
        <p className="mt-3 text-[13px] leading-relaxed text-slate-600">{t.body}</p>
        <div className="mt-2 rounded-lg bg-yono-paper px-3 py-2 text-[11px] text-slate-500">
          {lang === 'hi'
            ? 'केवल इस-डिवाइस विश्लेषण · कोई डेटा साझा नहीं · सहमति वापस ली जा सकती है'
            : 'On-device analysis only · no data shared · consent is revocable'}
        </div>
        <button
          onClick={onAllow}
          className="mt-4 w-full rounded-xl bg-yono-blue py-2.5 text-sm font-semibold text-white hover:bg-yono-blue/90"
        >
          {t.allow}
        </button>
        <button
          onClick={onDecline}
          className="mt-2 w-full rounded-xl py-2 text-[12px] font-medium text-slate-400 hover:text-slate-600"
        >
          {t.decline}
        </button>
      </div>
    </div>
  )
}
