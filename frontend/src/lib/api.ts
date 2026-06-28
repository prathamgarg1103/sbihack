// Thin API client. In dev, '/api/*' is proxied to the FastAPI backend
// (see vite.config.ts). Keep this the single place that knows the base URL.

const BASE = '/api'

export interface Persona {
  persona_id: string
  name: string
  headline: string
  flow: string
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
  suggested_category: string
  evidence: Record<string, unknown>
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

export interface Walkthrough {
  feature: string
  display: string
  steps: string[]
  time_seconds: number
}

export interface LadderRung {
  feature: string
  display: string
  adopted: boolean
}

export interface Ladder {
  ladder: LadderRung[]
  adopted: string[]
  next: string | null
  next_display: string | null
}

export interface Subscription {
  sub_id: string
  name: string
  category: string
  amount: number
  cadence: string
  via: string
  next_charge_in_days: number
  is_mandate?: boolean
}

export interface GoalRedirect {
  goal_id: string
  label: string
  amount: number
  saved_before: number
  saved_after: number
  target: number
  pct_before: number
  pct_after: number
  text: NudgeCopy
}

export interface InvestScenario {
  years: number
  invested: number
  rd_value: number
  sip_value: number
  sip_gain: number
}

export interface Invest {
  monthly: number
  rd_pct: number
  sip_pct: number
  scenarios: InvestScenario[]
  disclaimer: string
}

export interface LearnState {
  adopted: string[]
  skipped: string[]
  note: string
}

export interface Fund {
  name: string
  amc: string
  is_sbi: boolean
  category: string
  expense_ratio: number
  return_5y: number
}

export interface Stock {
  symbol: string
  name: string
  sector: string
  is_sbi: boolean
}

export interface InvestmentShelf {
  funds: Fund[]
  stocks: Stock[]
  fund_count: number
  stock_count: number
  sbi_fund_count: number
  other_fund_count: number
  neutrality_note: string
  honest_highlight: string
  illustrative: boolean
  disclaimer: string
  sources: string[]
}

export interface SweepRow {
  persona_id: string
  headline: string
  flow_label: string
  action: 'surface' | 'suppress' | 'stay_silent'
  surfaced_trigger: string | null
  rationale: string
  engine: string
}

export interface AgentDecision {
  action: 'surface' | 'suppress' | 'stay_silent'
  flow?: 'product' | 'feature_discovery' | 'subscription' | 'invest_shelf'
  surfaced_moment?: Moment | null
  investment_shelf?: InvestmentShelf | null
  product?: { type: string; doc_id: string; monthly_cost: number }
  suitability?: { suitable: boolean; blocks: string[]; reasons: string[] }
  comparison_available?: boolean
  neutral_disclosure?: boolean
  // feature_discovery
  walkthrough?: Walkthrough
  ladder?: Ladder
  unlocks?: string | null
  // subscription
  subscriptions?: Subscription[]
  flagged?: Subscription
  is_mandate?: boolean
  total_monthly?: number
  potential_savings?: number
  goal_redirect?: GoalRedirect | null
  invest?: Invest | null
  nudge?: { title: NudgeCopy; body: NudgeCopy; cta: NudgeCopy }
  suppressed?: Suppressed[]
  decision_log: DecisionStep[]
  learn_state?: LearnState
  engine: string
  model?: string
  llm_error?: string
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
  sweep: () => get<{ generated_at: string; engine: string; rows: SweepRow[] }>('/agent/sweep'),
  feedback: (
    persona_id: string,
    trigger_type: string,
    outcome: 'adopted' | 'skipped' | 'escalated',
    detail?: string,
  ) =>
    post<{ recorded: unknown; summary: Record<string, number> }>('/feedback', {
      persona_id,
      trigger_type,
      outcome,
      detail,
    }),
  resetFeedback: (id: string) =>
    fetch(`/api/feedback/${id}`, { method: 'DELETE' }).then((r) => r.json()),
}
