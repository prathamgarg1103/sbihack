// Thin API client. In dev, '/api/*' is proxied to the FastAPI backend
// (see vite.config.ts). Keep this the single place that knows the base URL.

const BASE = '/api'

export interface Guardian {
  name: string
  relation: string
  relation_hi?: string
}

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
  assisted_mode?: boolean
  guardian?: Guardian
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
  do_nothing?: string
  winner: 'sbi' | 'competitor' | 'tie' | 'do_nothing'
}

export interface Comparison {
  product_type: string
  sbi_product: { name: string; insurer: string }
  competitor_product: { name: string; insurer: string }
  rows: ComparisonRow[]
  competitor_wins: string[]
  do_nothing_wins?: string[]
  do_nothing_note?: string
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

// --- Governance features -----------------------------------------------------
export interface DevilsAdvocate {
  objection: NudgeCopy
  strength: 'weak' | 'strong'
  score: number
  verdict: 'attach' | 'suppress'
  engine: string
}

export interface AttentionBudget {
  used: number
  cap: number
  remaining: number
  month: string
}

export interface DoNothing {
  label: NudgeCopy
  detail: NudgeCopy
  honest_note: NudgeCopy
  savings_rate_pct: number
  inflation_pct: number
  yearly_real_loss: number
  source: string
}

export interface ExitAnalysis {
  product: string
  insurer: string
  monthly_premium: number
  annual_premium: number
  months_paid: number
  paid_so_far: number
  free_look: { days: number; within_window: boolean; note: NudgeCopy }
  exit_now: {
    surrender_charge: number
    fund_value_estimate: number
    refund_estimate: number
    locked_until_year: number
    discontinued_fund_pct: number
    note: NudgeCopy
  }
  stay: {
    annual_premium: number
    charges_pct_yr: number
    lock_in_years: number
    note: NudgeCopy
    wins: string[]
  }
  sources: string[]
  disclaimer: string
}

export interface CoconsentGate {
  required: boolean
  threshold: number
  amount: number
  action: string
  guardian: Guardian
  note: NudgeCopy
}

export interface CoconsentRequest {
  id: string
  persona_id: string
  action: string
  amount: number
  guardian_name: string | null
  guardian_relation: string | null
  status: 'pending' | 'approved' | 'declined'
  created_ts: string
  decided_ts: string | null
}

export interface AuditPayload {
  suitability?: { suitable: boolean | null; blocks: string[] | null; reasons: string[] | null } | null
  devils_advocate?: { objection: string | null; strength: string | null; verdict: string | null } | null
  consent_state?: string
  suppress_reasons?: string[] | null
  attention_budget?: AttentionBudget | null
  nudge_title?: string | null
  engine?: string
}

export interface AuditRecord {
  seq: number
  ts: string
  persona_id: string
  trigger_type: string
  product: string
  action: string
  payload: AuditPayload
  prev_hash: string
  hash: string
}

export interface AuditVerify {
  intact: boolean
  records: number
  broken_at: number | null
}

export interface AgentDecision {
  action: 'surface' | 'suppress' | 'stay_silent'
  flow?: 'product' | 'feature_discovery' | 'subscription' | 'invest_shelf' | 'missold'
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
  // governance features
  devils_advocate?: DevilsAdvocate
  attention_budget?: AttentionBudget
  budget_suppressed?: boolean
  do_nothing?: DoNothing
  exit_analysis?: ExitAnalysis | null
  coconsent?: CoconsentGate
  reason?: string[]
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
  budget: (id: string) => get<AttentionBudget>(`/personas/${id}/budget`),
  coconsentRequest: (persona_id: string, action: string, amount: number) =>
    post<{ required: boolean; request?: CoconsentRequest }>('/coconsent/request', {
      persona_id,
      action,
      amount,
    }),
  coconsentDecide: (id: string, approve: boolean) =>
    post<CoconsentRequest>(`/coconsent/${id}/${approve ? 'approve' : 'decline'}`, {}),
  audit: (limit = 100) =>
    get<{ verify: AuditVerify; records: AuditRecord[] }>(`/audit?limit=${limit}`),
}
