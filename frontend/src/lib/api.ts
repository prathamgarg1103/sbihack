// Thin API client. In dev, '/api/*' is proxied to the FastAPI backend
// (see vite.config.ts). Keep this the single place that knows the base URL.

const BASE = '/api'

export interface Persona {
  persona_id: string
  name: string
  headline: string
  flow: 'A' | 'B' | 'C'
  blurb: string
  language_pref: 'en' | 'hi'
  monthly_income: number
  current_balance: number
  transaction_count: number
}

export interface Txn {
  txn_id: string
  timestamp: string
  amount: number
  payee_name: string
  payee_category_truth: string
  channel: string
  balance_after: number
}

export interface Moment {
  trigger_type: string
  persona_id: string
  title: string
  summary: string
  severity: 'low' | 'medium' | 'high'
  suggested_category: 'fixed_deposit' | 'insurance_compare' | 'micro_cover'
  evidence: Record<string, string | number>
  evidence_txn_ids: string[]
}

export interface ComparisonRow {
  dimension: string
  sbi: string
  competitor: string
  winner: 'sbi' | 'competitor' | 'tie'
}

export interface Comparison {
  product_type: string
  sbi_product: { name: string; insurer: string }
  competitor_product: { name: string; insurer: string }
  rows: ComparisonRow[]
  competitor_wins: string[]
  annual_saving: number | null
  verdict: string
  sources: string[]
  disclaimer: string
}

export interface NudgeCopy {
  en: string
  hi: string
}

export interface DecisionStep {
  step: string
  tool?: string | null
  detail: string
  result?: unknown
}

export interface Suppressed {
  trigger_type: string
  reason: string
}

export interface AgentDecision {
  action: 'surface' | 'suppress' | 'stay_silent'
  surfaced_moment?: Moment | null
  product?: { type: string; doc_id: string; monthly_cost: number }
  suitability?: { suitable: boolean; blocks: string[]; reasons: string[] }
  comparison_available?: boolean
  nudge?: { title: NudgeCopy; body: NudgeCopy; cta: NudgeCopy }
  suppressed?: Suppressed[]
  decision_log: DecisionStep[]
  engine: string
  model?: string
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} on ${path}`)
  return res.json() as Promise<T>
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} on ${path}`)
  return res.json() as Promise<T>
}

export const api = {
  health: () => get<{ status: string; model: string; anthropic_key_present: boolean }>('/health'),
  personas: () => get<Persona[]>('/personas'),
  transactions: (id: string) =>
    get<{ persona_id: string; count: number; transactions: Txn[] }>(
      `/personas/${id}/transactions`,
    ),
  triggers: (id: string) =>
    get<{ persona_id: string; count: number; moments: Moment[] }>(
      `/personas/${id}/triggers`,
    ),
  comparison: (id: string) =>
    get<{ persona_id: string; trigger: Moment; comparison: Comparison }>(
      `/personas/${id}/comparison`,
    ),
  nudge: (id: string) => get<AgentDecision>(`/personas/${id}/nudge`),
  feedback: (persona_id: string, trigger_type: string, outcome: 'adopted' | 'skipped' | 'escalated') =>
    post<{ recorded: unknown; summary: Record<string, number> }>('/feedback', {
      persona_id,
      trigger_type,
      outcome,
    }),
  resetFeedback: (id: string) =>
    fetch(`/api/feedback/${id}`, { method: 'DELETE' }).then((r) => r.json()),
}
