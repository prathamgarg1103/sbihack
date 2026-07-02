import { useEffect, useState } from 'react'
import { api, type AuditRecord, type AuditVerify, type SweepRow } from '../lib/api'

const ACTION_STYLE: Record<string, { label: string; text: string; dot: string; chip: string }> = {
  surface: { label: 'NUDGE SENT', text: 'text-yono-mint', dot: 'bg-yono-mint', chip: 'bg-yono-mint/15 text-yono-mint' },
  suppress: { label: 'HELD BACK', text: 'text-yono-amber', dot: 'bg-yono-amber', chip: 'bg-yono-amber/15 text-yono-amber' },
  stay_silent: { label: 'STAYED SILENT', text: 'text-slate-400', dot: 'bg-slate-300', chip: 'bg-slate-100 text-slate-400' },
}

function initials(headline: string): string {
  return headline.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase()
}

function short(hash: string): string {
  return `${hash.slice(0, 8)}…${hash.slice(-6)}`
}

/** One expandable record of the hash-chained suitability-certificate trail. */
function AuditRow({ r }: { r: AuditRecord }) {
  const [open, setOpen] = useState(false)
  const style = ACTION_STYLE[r.action] ?? ACTION_STYLE.stay_silent
  const p = r.payload ?? {}
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-3 px-3 py-2.5 text-left"
      >
        <span className="w-8 shrink-0 text-[10px] font-bold text-slate-500">#{r.seq}</span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <p className="truncate text-[12px] font-semibold text-white">{r.persona_id}</p>
            <span className={`rounded-full px-1.5 py-0.5 text-[8px] font-bold uppercase ${style.chip}`}>
              {style.label}
            </span>
          </div>
          <p className="truncate text-[11px] text-slate-400">
            {r.trigger_type} · {r.product} ·{' '}
            {new Date(r.ts).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
        <span className="shrink-0 text-[10px] text-slate-500">{open ? '▾' : '▸'}</span>
      </button>
      {open && (
        <div className="space-y-1.5 border-t border-white/10 px-3 py-2.5 text-[11px]">
          {p.nudge_title && (
            <p className="text-slate-300">
              <span className="font-bold text-slate-500">nudge · </span>
              {p.nudge_title}
            </p>
          )}
          {p.suitability && (
            <p className="text-slate-300">
              <span className="font-bold text-slate-500">suitability · </span>
              {p.suitability.suitable
                ? 'suitable'
                : `blocked: ${(p.suitability.blocks ?? []).join('; ') || 'n/a'}`}
            </p>
          )}
          {p.devils_advocate?.objection && (
            <p className="text-slate-300">
              <span className="font-bold text-rose-400">devil's advocate · </span>“
              {p.devils_advocate.objection}” → {p.devils_advocate.verdict}
            </p>
          )}
          {p.suppress_reasons && p.suppress_reasons.length > 0 && (
            <p className="text-slate-300">
              <span className="font-bold text-yono-amber">suppressed · </span>
              {p.suppress_reasons.join('; ')}
            </p>
          )}
          <p className="text-slate-300">
            <span className="font-bold text-slate-500">consent · </span>
            {p.consent_state ?? 'n/a'}
            <span className="ml-3 font-bold text-slate-500">engine · </span>
            {p.engine ?? '?'}
          </p>
          <p className="break-all font-mono text-[9px] text-slate-500">
            prev {short(r.prev_hash)} → this {short(r.hash)}
          </p>
        </div>
      )}
    </div>
  )
}

/** The regulator view: every decision, chained and verifiable. */
function ComplianceTab() {
  const [records, setRecords] = useState<AuditRecord[]>([])
  const [verify, setVerify] = useState<AuditVerify | null>(null)
  const [error, setError] = useState('')

  function load() {
    api
      .audit()
      .then((r) => {
        setRecords(r.records.slice().reverse()) // newest first
        setVerify(r.verify)
      })
      .catch((e) => setError(String(e)))
  }
  useEffect(load, [])

  return (
    <div className="px-4 pb-4">
      <div className="mb-3 flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-3 py-2.5">
        {verify ? (
          verify.intact ? (
            <span className="flex items-center gap-2 text-[12px] font-semibold text-yono-mint">
              ✓ chain verified · {verify.records} records · SHA-256 linked
            </span>
          ) : (
            <span className="flex items-center gap-2 text-[12px] font-semibold text-rose-400">
              ⚠ TAMPERED — chain broken at record #{verify.broken_at}
            </span>
          )
        ) : (
          <span className="text-[12px] text-slate-400">Verifying chain…</span>
        )}
        <button
          onClick={load}
          className="rounded-lg border border-white/15 px-2.5 py-1 text-[11px] font-semibold text-slate-200 hover:bg-white/10"
        >
          Re-verify
        </button>
      </div>
      {error && (
        <p className="rounded-xl bg-amber-500/10 px-3 py-2 text-[12px] text-amber-300">
          Couldn't reach the backend ({error}).
        </p>
      )}
      {!error && records.length === 0 && (
        <p className="px-1 py-3 text-[12px] text-slate-400">
          No decisions recorded yet — run a nudge or a sweep first. Every decision
          (surfaced or suppressed) joins the chain automatically.
        </p>
      )}
      <div className="space-y-2">
        {records.map((r) => (
          <AuditRow key={r.seq} r={r} />
        ))}
      </div>
      <p className="mt-3 px-1 text-[11px] text-slate-400">
        Suitability certificate: SBI can hand a regulator a per-recommendation,
        tamper-evident audit trail — trigger, verdict, objection, consent, action.
      </p>
    </div>
  )
}

export function MissionControl() {
  const [tab, setTab] = useState<'feed' | 'compliance'>('feed')
  const [rows, setRows] = useState<SweepRow[]>([])
  const [engine, setEngine] = useState('')
  const [revealed, setRevealed] = useState(0)
  const [scanning, setScanning] = useState(true)
  const [error, setError] = useState('')

  function run() {
    setError('')
    setRows([])
    setRevealed(0)
    setScanning(true)
    api
      .sweep()
      .then((r) => {
        setRows(r.rows)
        setEngine(r.engine)
      })
      .catch((e) => setError(String(e)))
  }

  useEffect(() => {
    run()
  }, [])

  // Staggered reveal for a live "ops feed" feel.
  useEffect(() => {
    if (!rows.length) return
    setRevealed(0)
    setScanning(true)
    let i = 0
    const id = setInterval(() => {
      i += 1
      setRevealed(i)
      if (i >= rows.length) {
        clearInterval(id)
        setScanning(false)
      }
    }, 480)
    return () => clearInterval(id)
  }, [rows])

  const live = engine === 'anthropic'
  const surfaced = rows.filter((r) => r.action === 'surface').length
  const suppressed = rows.filter((r) => r.action !== 'surface').length

  return (
    <div className="w-full max-w-3xl">
      <div className="overflow-hidden rounded-3xl border border-slate-200 bg-yono-ink shadow-2xl">
        {/* Console header */}
        <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-yono-blue to-yono-mint text-sm font-bold text-white">
              ✦
            </div>
            <div>
              <p className="text-sm font-bold text-white">Diya Mission Control</p>
              <p className="text-[11px] text-slate-400">
                One agent · every user · the loop running at fleet scale
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex overflow-hidden rounded-lg border border-white/15 text-[10px] font-bold">
              {(['feed', 'compliance'] as const).map((v) => (
                <button
                  key={v}
                  onClick={() => setTab(v)}
                  className={`px-2.5 py-1 uppercase ${
                    tab === v ? 'bg-white/15 text-white' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {v === 'feed' ? 'Live feed' : 'Compliance'}
                </button>
              ))}
            </div>
            <span
              className={`rounded-full px-2 py-0.5 text-[9px] font-bold uppercase ${
                live ? 'bg-yono-mint/20 text-yono-mint' : 'bg-white/10 text-slate-300'
              }`}
            >
              {live ? 'LLM live' : 'rules'}
            </span>
            {tab === 'feed' && (
              <button
                onClick={run}
                className="rounded-lg border border-white/15 px-2.5 py-1 text-[11px] font-semibold text-slate-200 hover:bg-white/10"
              >
                Re-scan
              </button>
            )}
          </div>
        </div>

        {tab === 'compliance' ? (
          <div className="pt-3">
            <ComplianceTab />
          </div>
        ) : (
        <>
        {/* Status line */}
        <div className="flex items-center gap-2 px-5 py-2.5 text-[11px]">
          {scanning ? (
            <>
              <span className="h-1.5 w-1.5 animate-ping rounded-full bg-yono-mint" />
              <span className="text-slate-300">
                Scanning {rows.length || '…'} live users for adoption moments…
              </span>
            </>
          ) : (
            <span className="text-slate-300">
              Swept <b className="text-white">{rows.length}</b> users ·{' '}
              <b className="text-yono-mint">{surfaced}</b> nudged ·{' '}
              <b className="text-yono-amber">{suppressed}</b> held back — autonomously.
            </span>
          )}
        </div>

        {/* Feed */}
        <div className="space-y-2 px-4 pb-4">
          {error && (
            <p className="rounded-xl bg-amber-500/10 px-3 py-2 text-[12px] text-amber-300">
              Couldn’t reach the backend ({error}).
            </p>
          )}
          {rows.map((r, i) => {
            const style = ACTION_STYLE[r.action] ?? ACTION_STYLE.stay_silent
            const shown = i < revealed
            return (
              <div
                key={r.persona_id}
                className={`flex items-start gap-3 rounded-2xl border border-white/10 bg-white/5 px-3 py-2.5 transition-all duration-500 ${
                  shown ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0'
                }`}
              >
                <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-white/10 text-[11px] font-bold text-white">
                  {initials(r.headline)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="truncate text-[13px] font-semibold text-white">{r.headline}</p>
                    <span className={`rounded-full px-1.5 py-0.5 text-[8px] font-bold uppercase ${style.chip}`}>
                      {style.label}
                    </span>
                  </div>
                  <p className="truncate text-[11px] text-slate-400">{r.flow_label}</p>
                  <p className="mt-0.5 text-[12px] leading-snug text-slate-200">{r.rationale}</p>
                </div>
                <span className={`mt-1 h-2 w-2 shrink-0 rounded-full ${style.dot}`} />
              </div>
            )
          })}
        </div>
        </>
        )}

        {/* Scale tagline */}
        <div className="border-t border-white/10 px-5 py-3">
          <p className="text-[11px] text-slate-400">
            The same perceive→reason→act loop powers all five journeys here — and is reusable across
            YONO’s 100+ planned journeys. <span className="text-slate-300">That’s the scalability story.</span>
          </p>
        </div>
      </div>
    </div>
  )
}
