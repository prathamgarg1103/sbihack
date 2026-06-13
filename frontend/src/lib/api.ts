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

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
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
}
