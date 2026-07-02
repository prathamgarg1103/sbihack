import type { CoconsentGate, CoconsentRequest } from '../lib/api'

type Lang = 'en' | 'hi'

function rupee(n: number): string {
  return Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })
}

/** The mock "guardian's phone" — assisted-mode (Sahayak) co-consent. The demo
 *  driver taps approve/decline here; the main flow blocks until decided. */
export function GuardianPhone({
  gate,
  request,
  personaName,
  lang,
  onApprove,
  onDecline,
}: {
  gate: CoconsentGate
  request: CoconsentRequest
  personaName: string
  lang: Lang
  onApprove: () => void
  onDecline: () => void
}) {
  const g = gate.guardian
  const relation = lang === 'hi' ? (g.relation_hi ?? g.relation) : g.relation
  const decided = request.status !== 'pending'
  return (
    <div className="w-[260px] shrink-0">
      <p className="mb-2 text-center text-xs font-semibold uppercase tracking-wide text-slate-400">
        {lang === 'hi' ? 'अभिभावक का फ़ोन (मॉक)' : "Guardian's phone (mock)"}
      </p>
      <div className="relative h-[420px] w-[260px] overflow-hidden rounded-[2rem] border-8 border-yono-ink bg-slate-100 shadow-xl">
        <div className="absolute left-1/2 top-0 z-20 h-4 w-20 -translate-x-1/2 rounded-b-xl bg-yono-ink" />
        <div className="flex h-full flex-col px-3 pt-8">
          <p className="text-center text-[11px] font-semibold text-slate-500">{g.name}</p>
          {/* The co-approval notification */}
          <div className="mt-3 rounded-2xl bg-white p-3.5 shadow-lg ring-1 ring-slate-200">
            <div className="flex items-center gap-2">
              <div className="grid h-6 w-6 place-items-center rounded-full bg-gradient-to-br from-yono-blue to-yono-mint text-[10px] font-bold text-white">
                ✦
              </div>
              <span className="text-[12px] font-semibold text-yono-ink">Diya · YONO</span>
              <span className="ml-auto rounded-full bg-yono-blue/10 px-1.5 py-0.5 text-[8px] font-bold uppercase text-yono-blue">
                {lang === 'hi' ? 'सह-मंज़ूरी' : 'co-approval'}
              </span>
            </div>
            <p className="mt-2.5 text-[12px] leading-snug text-slate-700">
              {lang === 'hi'
                ? `${personaName} ₹${rupee(gate.amount)} से जुड़ा एक कदम उठाना चाहती हैं। ${relation} होने के नाते, क्या आप मंज़ूरी देते हैं?`
                : `${personaName} wants to proceed with a step involving ₹${rupee(gate.amount)}. As her ${relation}, do you approve?`}
            </p>
            <p className="mt-1.5 rounded-lg bg-yono-paper px-2 py-1.5 text-[10px] leading-snug text-slate-500">
              {gate.note[lang]}
            </p>

            {decided ? (
              <div
                className={`mt-3 rounded-xl px-3 py-2 text-center text-[12px] font-semibold ${
                  request.status === 'approved'
                    ? 'bg-yono-mint/15 text-yono-mint'
                    : 'bg-rose-100 text-rose-600'
                }`}
              >
                {request.status === 'approved'
                  ? lang === 'hi' ? '✓ मंज़ूर किया गया' : '✓ Approved'
                  : lang === 'hi' ? '✕ अस्वीकार किया गया' : '✕ Declined'}
              </div>
            ) : (
              <div className="mt-3 flex gap-2">
                <button
                  onClick={onApprove}
                  className="flex-1 rounded-xl bg-yono-mint py-2 text-[12px] font-semibold text-white hover:bg-yono-mint/90"
                >
                  {lang === 'hi' ? 'मंज़ूर करें' : 'Approve'}
                </button>
                <button
                  onClick={onDecline}
                  className="flex-1 rounded-xl border border-slate-200 py-2 text-[12px] font-medium text-slate-500 hover:border-slate-300"
                >
                  {lang === 'hi' ? 'अस्वीकार' : 'Decline'}
                </button>
              </div>
            )}
          </div>
          <p className="mt-3 text-center text-[10px] leading-snug text-slate-400">
            {lang === 'hi'
              ? 'सहायता-मोड: ₹10,000 से ऊपर के कदमों के लिए सह-मंज़ूरी'
              : 'Assisted mode: steps above ₹10,000 need co-approval'}
          </p>
        </div>
      </div>
    </div>
  )
}

/** Blocking card shown on the MAIN phone while the guardian decides. */
export function GuardianWait({
  gate,
  status,
  lang,
  onDismiss,
}: {
  gate: CoconsentGate
  status: 'pending' | 'declined'
  lang: Lang
  onDismiss: () => void
}) {
  const g = gate.guardian
  return (
    <div className="absolute inset-0 z-30 flex items-end bg-yono-ink/30 backdrop-blur-[1px]">
      <div className="m-3 w-full rounded-3xl bg-white p-5 shadow-2xl ring-1 ring-slate-200">
        <div className="flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-yono-blue to-yono-mint text-white">
            {status === 'pending' ? '⏳' : '🛡️'}
          </div>
          <span className="text-sm font-semibold text-yono-ink">
            {status === 'pending'
              ? lang === 'hi' ? 'सह-मंज़ूरी का इंतज़ार' : 'Waiting for co-approval'
              : lang === 'hi' ? 'अभिभावक ने अस्वीकार किया' : 'Guardian declined'}
          </span>
        </div>
        <p className="mt-3 text-[13px] leading-relaxed text-slate-600">
          {status === 'pending'
            ? lang === 'hi'
              ? `${g.name} (${g.relation_hi ?? g.relation}) के फ़ोन पर अनुरोध भेजा गया है। उनकी मंज़ूरी के बाद ही यह कदम आगे बढ़ेगा।`
              : `A request was sent to ${g.name} (${g.relation})'s phone. This step continues only after their approval.`
            : lang === 'hi'
              ? 'कोई बात नहीं — कुछ भी बदला नहीं गया। आप कभी भी सलाहकार से बात कर सकती हैं।'
              : 'No problem — nothing was changed. You can talk to a human advisor anytime.'}
        </p>
        {status === 'pending' ? (
          <div className="mt-3 flex items-center gap-2 rounded-lg bg-yono-paper px-3 py-2 text-[11px] text-slate-500">
            <span className="h-1.5 w-1.5 animate-ping rounded-full bg-yono-blue" />
            {lang === 'hi' ? 'मुख्य फ़्लो रुका हुआ है…' : 'Main flow is blocked…'}
          </div>
        ) : null}
        <button
          onClick={onDismiss}
          className="mt-4 w-full rounded-xl py-2 text-[12px] font-medium text-slate-400 hover:text-slate-600"
        >
          {status === 'pending'
            ? lang === 'hi' ? 'रद्द करें' : 'Cancel'
            : lang === 'hi' ? 'ठीक है' : 'OK'}
        </button>
      </div>
    </div>
  )
}
