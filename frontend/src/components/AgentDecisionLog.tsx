import type { AgentDecision, DecisionStep } from '../lib/api'

const STEP_STYLE: Record<string, { dot: string; label: string }> = {
  perceive: { dot: 'bg-slate-400', label: 'PERCEIVE' },
  reason: { dot: 'bg-yono-blue', label: 'REASON' },
  suppress: { dot: 'bg-yono-amber', label: 'SUPPRESS' },
  act: { dot: 'bg-yono-mint', label: 'ACT' },
}

function Result({ result }: { result: unknown }) {
  if (result == null) return null
  const text = Array.isArray(result) ? result.join(', ') : String(result)
  return <span className="text-slate-500"> → {text}</span>
}

function Step({ s }: { s: DecisionStep }) {
  const style = STEP_STYLE[s.step] ?? { dot: 'bg-slate-300', label: s.step.toUpperCase() }
  return (
    <li className="relative pl-5">
      <span className={`absolute left-0 top-1.5 h-2 w-2 rounded-full ${style.dot}`} />
      <div className="flex items-center gap-1.5">
        <span className="text-[9px] font-bold tracking-wide text-slate-400">{style.label}</span>
        {s.tool && (
          <code className="rounded bg-yono-blue/10 px-1 text-[10px] font-semibold text-yono-blue">
            {s.tool}()
          </code>
        )}
      </div>
      <p className="text-[12px] leading-snug text-slate-700">
        {s.detail}
        <Result result={s.result} />
      </p>
    </li>
  )
}

export function AgentDecisionLog({ decision }: { decision: AgentDecision }) {
  const live = decision.engine === 'anthropic'
  return (
    <aside className="w-[320px] shrink-0">
      <div className="mb-2 flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          Agent decision loop
        </p>
        <span
          className={`rounded-full px-2 py-0.5 text-[9px] font-bold uppercase ${
            live ? 'bg-yono-mint/15 text-yono-mint' : 'bg-slate-200 text-slate-500'
          }`}
          title={decision.model}
        >
          {live ? 'LLM live' : 'rules'}
        </span>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-4">
        <ol className="space-y-2.5 border-l border-dashed border-slate-200 pl-1">
          {decision.decision_log.map((s, i) => (
            <Step key={i} s={s} />
          ))}
        </ol>

        {/* Outcome chip */}
        <div className="mt-3 border-t border-slate-100 pt-3">
          <span
            className={`rounded-lg px-2 py-1 text-[11px] font-semibold ${
              decision.action === 'surface'
                ? 'bg-yono-mint/12 text-yono-ink'
                : 'bg-slate-100 text-slate-500'
            }`}
          >
            outcome: {decision.action}
          </span>
          {decision.suppressed && decision.suppressed.length > 0 && (
            <p className="mt-2 text-[11px] text-slate-400">
              suppressed {decision.suppressed.map((s) => s.trigger_type).join(', ')}
            </p>
          )}
        </div>

        {/* Adoption ladder (platform depth) */}
        {decision.ladder && (
          <div className="mt-3 border-t border-slate-100 pt-3">
            <p className="text-[9px] font-bold uppercase tracking-wide text-slate-400">
              Adoption ladder
            </p>
            <div className="mt-1.5 flex items-center gap-1">
              {decision.ladder.ladder.map((rung, idx) => (
                <div key={rung.feature} className="flex items-center gap-1">
                  <span
                    className={`rounded px-1.5 py-0.5 text-[9px] font-semibold ${
                      rung.adopted
                        ? 'bg-yono-mint/20 text-yono-mint'
                        : rung.feature === decision.ladder!.next
                          ? 'bg-yono-blue/10 text-yono-blue ring-1 ring-yono-blue'
                          : 'bg-slate-100 text-slate-400'
                    }`}
                  >
                    {rung.adopted ? '✓ ' : ''}
                    {rung.display}
                  </span>
                  {idx < decision.ladder!.ladder.length - 1 && (
                    <span className="text-[9px] text-slate-300">→</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <p className="mt-2 text-[10px] leading-relaxed text-slate-400">
        {live
          ? `Reasoned live by ${decision.model}.`
          : 'Running the rule-based fallback. Add an ANTHROPIC_API_KEY to see the LLM reason and write the copy itself.'}
      </p>
    </aside>
  )
}
