import { useEffect, useState } from 'react'
import {
  api,
  type AgentDecision,
  type Comparison,
  type Persona,
  type Txn,
} from './lib/api'
import { NudgeCard } from './components/NudgeCard'
import { ComparisonTable } from './components/ComparisonTable'
import { ConsentGate } from './components/ConsentGate'
import { AgentDecisionLog } from './components/AgentDecisionLog'
import { CoachmarkWalkthrough } from './components/CoachmarkWalkthrough'
import { SubscriptionDashboard } from './components/SubscriptionDashboard'

type Lang = 'en' | 'hi'

const FLOW_LABEL: Record<string, string> = {
  A: 'Idle balance → Sweep FD',
  B: 'Premium leak → Honest compare',
  C: 'Salary jump → Micro-cover',
  D: 'Feature blind-spot → Guided discovery',
  S: 'Subscriptions → Save & redirect',
}

const QUICK_ACTIONS = ['Scan & Pay', 'To Mobile', 'To Bank A/C', 'Balance', 'Recharge', 'Bills']

function rupee(n: number): string {
  return n.toLocaleString('en-IN', { maximumFractionDigits: 0 })
}

function PhoneFrame({
  children,
  overlay,
}: {
  children: React.ReactNode
  overlay?: React.ReactNode
}) {
  return (
    <div className="relative h-[760px] w-[380px] overflow-hidden rounded-[2.5rem] border-[10px] border-yono-ink bg-white shadow-2xl">
      <div className="absolute left-1/2 top-0 z-20 h-6 w-32 -translate-x-1/2 rounded-b-2xl bg-yono-ink" />
      <div className="h-full overflow-y-auto">{children}</div>
      {overlay}
    </div>
  )
}

function TxnRow({ t }: { t: Txn }) {
  const debit = t.amount < 0
  return (
    <div className="flex items-center justify-between border-b border-slate-100 py-2.5">
      <div className="min-w-0">
        <p className="truncate text-sm font-medium text-yono-ink">{t.payee_name}</p>
        <p className="text-xs text-slate-400">
          {new Date(t.timestamp).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })} ·{' '}
          {t.channel}
        </p>
      </div>
      <span className={`shrink-0 text-sm font-semibold ${debit ? 'text-yono-ink' : 'text-yono-mint'}`}>
        {debit ? '−' : '+'}₹{rupee(Math.abs(t.amount))}
      </span>
    </div>
  )
}

export default function App() {
  const [personas, setPersonas] = useState<Persona[]>([])
  const [activeId, setActiveId] = useState<string>('')
  const [txns, setTxns] = useState<Txn[]>([])
  const [decision, setDecision] = useState<AgentDecision | null>(null)
  const [lang, setLang] = useState<Lang>('en')
  const [consented, setConsented] = useState(false)
  const [skipped, setSkipped] = useState(false)
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [walkthroughOpen, setWalkthroughOpen] = useState(false)
  const [subscriptionOpen, setSubscriptionOpen] = useState(false)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    api
      .personas()
      .then((ps) => {
        setPersonas(ps)
        if (ps.length) setActiveId(ps[0].persona_id)
      })
      .catch((e) => setError(String(e)))
  }, [])

  useEffect(() => {
    if (!activeId) return
    setSkipped(false)
    setConsented(false)
    setComparison(null)
    setWalkthroughOpen(false)
    setSubscriptionOpen(false)
    setDecision(null)
    const persona = personas.find((p) => p.persona_id === activeId)
    if (persona) setLang(persona.language_pref)
    api
      .transactions(activeId)
      .then((r) => setTxns(r.transactions.slice().reverse()))
      .catch((e) => setError(String(e)))
    refetchNudge()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeId, personas])

  function refetchNudge() {
    if (!activeId) return
    api
      .nudge(activeId)
      .then(setDecision)
      .catch((e) => setError(String(e)))
  }

  const active = personas.find((p) => p.persona_id === activeId)

  function record(outcome: 'adopted' | 'skipped' | 'escalated') {
    const tt = decision?.surfaced_moment?.trigger_type
    if (activeId && tt) api.feedback(activeId, tt, outcome).catch(() => {})
  }

  function handleSkip() {
    record('skipped') // teaches the agent to suppress this category next time
    setSkipped(true)
  }

  function handlePrimary() {
    const cat = decision?.surfaced_moment?.suggested_category
    if (cat === 'insurance_compare') {
      record('adopted')
      api
        .comparison(activeId)
        .then((r) => setComparison(r.comparison))
        .catch((e) => setError(String(e)))
    } else if (cat === 'feature_discovery') {
      setWalkthroughOpen(true) // adoption is recorded when the walkthrough completes
    } else if (cat === 'subscription_review') {
      setSubscriptionOpen(true)
    } else {
      record('adopted')
    }
  }

  function adoptFeature() {
    const feature = decision?.walkthrough?.feature
    if (activeId) api.feedback(activeId, 'feature_discovery', 'adopted', feature).catch(() => {})
    setWalkthroughOpen(false)
    refetchNudge() // ladder advances; agent moves past the adopted feature
  }

  function redirectSavings() {
    if (activeId) api.feedback(activeId, 'subscription_saver', 'adopted', decision?.flagged?.sub_id).catch(() => {})
    setSubscriptionOpen(false)
    refetchNudge()
  }

  const showNudge = decision?.action === 'surface' && decision.surfaced_moment && !skipped

  let overlay: React.ReactNode = null
  if (comparison) {
    overlay = <ComparisonTable data={comparison} onBack={() => setComparison(null)} />
  } else if (walkthroughOpen && decision?.walkthrough) {
    overlay = (
      <CoachmarkWalkthrough
        walkthrough={decision.walkthrough}
        lang={lang}
        onAdopt={adoptFeature}
        onClose={() => setWalkthroughOpen(false)}
      />
    )
  } else if (subscriptionOpen && decision) {
    overlay = (
      <SubscriptionDashboard
        decision={decision}
        lang={lang}
        onClose={() => setSubscriptionOpen(false)}
        onRedirect={redirectSavings}
      />
    )
  } else if (showNudge && decision) {
    overlay = consented ? (
      <NudgeCard
        decision={decision}
        lang={lang}
        onLang={setLang}
        onSkip={handleSkip}
        onPrimary={handlePrimary}
      />
    ) : (
      <ConsentGate
        moment={decision.surfaced_moment!}
        lang={lang}
        onAllow={() => setConsented(true)}
        onDecline={handleSkip}
      />
    )
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-7xl flex-col items-center gap-8 px-6 py-10">
      <header className="text-center">
        <h1 className="text-3xl font-bold tracking-tight text-yono-ink">
          Saarthi <span className="text-yono-blue">·</span>{' '}
          <span className="font-medium text-slate-500">Agentic Adoption Copilot</span>
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Trust-first nudges inside a mocked YONO super-app · synthetic data only
        </p>
      </header>

      {error && (
        <div className="rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Couldn’t reach the backend ({error}). Start it with{' '}
          <code className="rounded bg-amber-100 px-1">uvicorn main:app --reload</code> in{' '}
          <code className="rounded bg-amber-100 px-1">/backend</code>.
        </div>
      )}

      <div className="flex flex-col items-center gap-6 lg:flex-row lg:items-start">
        {/* Persona switcher */}
        <aside className="w-[280px] shrink-0">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Demo persona
          </p>
          <div className="flex flex-col gap-2">
            {personas.map((p) => {
              const on = p.persona_id === activeId
              return (
                <button
                  key={p.persona_id}
                  onClick={() => setActiveId(p.persona_id)}
                  className={`rounded-xl border px-4 py-3 text-left transition ${
                    on
                      ? 'border-yono-blue bg-yono-blue/5 ring-1 ring-yono-blue'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-yono-ink">{p.headline}</span>
                    <span className="rounded-full bg-yono-ink px-2 py-0.5 text-[10px] font-bold text-white">
                      FLOW {p.flow}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">{p.blurb}</p>
                  <p className="mt-1.5 text-[11px] font-medium text-yono-blue">{FLOW_LABEL[p.flow]}</p>
                </button>
              )
            })}
          </div>
        </aside>

        {/* The mocked YONO phone */}
        <PhoneFrame overlay={overlay}>
          {active && (
            <div className="flex min-h-full flex-col bg-gradient-to-b from-yono-blue to-yono-sky">
              <div className="flex items-center justify-between px-5 pb-3 pt-9 text-white">
                <div>
                  <p className="text-xs/none opacity-80">Good morning</p>
                  <p className="text-lg font-semibold">{active.name}</p>
                </div>
                <div className="grid h-9 w-9 place-items-center rounded-full bg-white/20 text-sm font-bold">
                  {active.name.split(' ').map((s) => s[0]).join('')}
                </div>
              </div>

              <div className="mx-5 rounded-2xl bg-white/15 p-4 text-white backdrop-blur">
                <p className="text-xs opacity-80">Savings A/C ···{active.persona_id.slice(-2)}21</p>
                <p className="mt-1 text-3xl font-bold">₹{rupee(active.current_balance)}</p>
                <p className="mt-1 text-[11px] opacity-75">
                  {active.transaction_count} transactions · earning 2.70% p.a.
                </p>
              </div>

              <div className="mt-4 flex-1 rounded-t-3xl bg-white px-5 pt-5">
                <div className="grid grid-cols-3 gap-3">
                  {QUICK_ACTIONS.map((q) => (
                    <div key={q} className="flex flex-col items-center gap-1.5">
                      <div className="grid h-12 w-12 place-items-center rounded-2xl bg-yono-paper text-yono-blue">
                        <span className="text-[10px] font-bold">UPI</span>
                      </div>
                      <span className="text-center text-[11px] leading-tight text-slate-600">{q}</span>
                    </div>
                  ))}
                </div>

                <div className="mt-5">
                  <div className="flex items-center justify-between">
                    <h2 className="text-sm font-semibold text-yono-ink">Recent activity</h2>
                    <span className="text-xs text-yono-blue">See all</span>
                  </div>
                  <div className="mt-1">
                    {txns.slice(0, 8).map((t) => (
                      <TxnRow key={t.txn_id} t={t} />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </PhoneFrame>

        {/* Agent decision loop */}
        {decision && <AgentDecisionLog decision={decision} />}
      </div>

      <footer className="text-xs text-slate-400">
        Perceive → reason → act loop · grounded in a cited corpus · ULIPs auto-blocked · synthetic data
      </footer>
    </div>
  )
}
