"""Synthetic data generator for Saarthi.

Produces a deterministic, reproducible transaction stream for three seeded
personas, each engineered to fire exactly one of the demo flows:

  * Persona 1 — Idle Saver     -> Flow A (idle balance -> sweep FD)
  * Persona 2 — Premium Leaker -> Flow B (competitor premium -> honest compare)
  * Persona 3 — New Earner     -> Flow C (salary jump / travel -> micro-cover)

No real PII, no real money. Run:  python data/generate.py
Output:  data/transactions.json
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Deterministic anchor so the demo is reproducible (today, per project context).
REF = datetime(2026, 6, 14, 9, 0, 0)
SEED = 42
OUT_PATH = Path(__file__).resolve().parent / "transactions.json"

CATEGORIES = {"premium", "salary", "merchant", "transfer", "bill"}
CHANNELS = {"UPI", "NACH", "IMPS", "card"}


class Ledger:
    """Builds a chronologically-ordered, balance-consistent txn list."""

    def __init__(self, persona_id: str, opening_balance: float):
        self.persona_id = persona_id
        self.balance = opening_balance
        self._rows: list[dict] = []
        self._n = 0

    def add(
        self,
        days_ago: float,
        amount: float,
        payee: str,
        category: str,
        channel: str,
    ) -> None:
        assert category in CATEGORIES, category
        assert channel in CHANNELS, channel
        ts = REF - timedelta(days=days_ago)
        self.balance = round(self.balance + amount, 2)
        self._n += 1
        self._rows.append(
            {
                "txn_id": f"{self.persona_id}-{self._n:04d}",
                "timestamp": ts.isoformat(),
                "amount": round(amount, 2),
                "payee_name": payee,
                "payee_category_truth": category,
                "channel": channel,
                "balance_after": self.balance,
            }
        )

    def rows(self) -> list[dict]:
        # Sort ascending by time, then recompute balances so they stay coherent
        # regardless of the order we appended in.
        ordered = sorted(self._rows, key=lambda r: r["timestamp"])
        running = self._opening()
        for r in ordered:
            running = round(running + r["amount"], 2)
            r["balance_after"] = running
        return ordered

    def _opening(self) -> float:
        # opening = first stored balance minus its own amount
        if not self._rows:
            return self.balance
        first = min(self._rows, key=lambda r: r["timestamp"])
        return round(first["balance_after"] - first["amount"], 2)


def _spends(led: Ledger, rng: random.Random, start_days: int, end_days: int, n: int,
            lo: int, hi: int) -> None:
    """Sprinkle small everyday UPI merchant debits across a window."""
    merchants = [
        "ZOMATO", "SWIGGY", "BIG BAZAAR", "JIO RECHARGE", "BESCOM ELECTRICITY",
        "AMAZON PAY", "IRCTC", "DMART", "BLINKIT", "UBER",
    ]
    bill_hints = ("RECHARGE", "ELECTRICITY", "GAS", "DTH", "BROADBAND")
    for _ in range(n):
        d = rng.uniform(end_days, start_days)
        amt = -float(rng.randint(lo, hi))
        payee = rng.choice(merchants)
        # Truth label follows the payee name, so it stays self-consistent.
        cat = "bill" if any(h in payee for h in bill_hints) else "merchant"
        led.add(d, amt, payee, cat, "UPI")


def persona_idle_saver(rng: random.Random) -> dict:
    """₹40k+ sits untouched for 90+ days; only small UPI debits move."""
    pid = "p1_idle_saver"
    led = Ledger(pid, opening_balance=50000.0)
    # A lump sits from 150 days ago and essentially never moves.
    led.add(150, 0.0, "OPENING BALANCE", "transfer", "IMPS")
    # Salary lands and is fully swept to another account -> savings buffer is left
    # untouched, so ~Rs.48k stays idle for 90+ days.
    for m in range(5, 0, -1):
        led.add(m * 30 + 2, 58000.0, "INFOSYS LTD SALARY", "salary", "NACH")
        led.add(m * 30 + 1, -58000.0, "SELF A/C 5521 TRANSFER", "transfer", "IMPS")
    # Only tiny day-to-day UPI debits over the last ~100 days (buffer stays high).
    _spends(led, rng, start_days=100, end_days=2, n=10, lo=100, hi=500)
    return {
        "persona_id": pid,
        "name": "Aarti Sharma",
        "headline": "Idle Saver",
        "flow": "A",
        "blurb": "Large balance sitting idle for 90+ days; touches only UPI + balance check.",
        "language_pref": "hi",
        "monthly_income": 58000,
        "ledger": led,
    }


def persona_premium_leaker(rng: random.Random) -> dict:
    """Recurring ₹1,240/mo to a competitor life insurer (the hero flow)."""
    pid = "p2_premium_leaker"
    led = Ledger(pid, opening_balance=18500.0)
    for m in range(12, 0, -1):
        led.add(m * 30 + 5, 46000.0, "TCS LTD SALARY", "salary", "NACH")
        # The leak: same competitor premium, same amount, every month.
        led.add(m * 30 + 3, -1240.0, "HDFC LIFE PREMIUM", "premium", "NACH")
        led.add(m * 30 + 1, -38000.0, "RENT GODREJ APTS", "transfer", "IMPS")
    _spends(led, rng, start_days=360, end_days=2, n=60, lo=150, hi=2600)
    return {
        "persona_id": pid,
        "name": "Rahul Verma",
        "headline": "Premium Leaker",
        "flow": "B",
        "blurb": "Pays a recurring premium to a competitor insurer every month.",
        "language_pref": "hi",
        "monthly_income": 46000,
        "ledger": led,
    }


def persona_new_earner(rng: random.Random) -> dict:
    """Salary jump + a recent MakeMyTrip travel spend."""
    pid = "p3_new_earner"
    led = Ledger(pid, opening_balance=9000.0)
    # Old salary band.
    led.add(95, 35000.0, "ACME CORP SALARY", "salary", "NACH")
    led.add(65, 35000.0, "ACME CORP SALARY", "salary", "NACH")
    # The jump (promotion / job switch).
    led.add(35, 55000.0, "ACME CORP SALARY", "salary", "NACH")
    led.add(5, 55000.0, "ACME CORP SALARY", "salary", "NACH")
    # Contextual travel spend on card, very recent.
    led.add(8, -18500.0, "MAKEMYTRIP", "merchant", "card")
    _spends(led, rng, start_days=95, end_days=1, n=30, lo=200, hi=3200)
    return {
        "persona_id": pid,
        "name": "Sneha Iyer",
        "headline": "New Earner",
        "flow": "C",
        "blurb": "Recent salary jump and a travel booking — a contextual cover moment.",
        "language_pref": "en",
        "monthly_income": 55000,
        "ledger": led,
    }


def persona_explorer(rng: random.Random) -> dict:
    """Flow D (hero): narrow YONO usage + a bill paid through another app."""
    pid = "p4_explorer"
    led = Ledger(pid, opening_balance=9000.0)
    for m in range(4, 0, -1):
        led.add(m * 30 + 2, 30000.0, "RELIANCE RETAIL SALARY", "salary", "NACH")
        # Electricity bill paid via a NON-YONO app every month (the blind spot).
        led.add(m * 30 + 6, -1180.0, "BESCOM ELECTRICITY", "bill", "UPI")
        led.add(m * 30 + 1, -27000.0, "SELF UPI WITHDRAWAL", "transfer", "UPI")
    _spends(led, rng, start_days=110, end_days=2, n=26, lo=80, hi=700)
    return {
        "persona_id": pid,
        "name": "Vikram Singh",
        "headline": "Explorer",
        "flow": "D",
        "blurb": "Uses YONO only for UPI + balance; pays bills in another app.",
        "language_pref": "hi",
        "monthly_income": 30000,
        # Platform-adoption signals (read by the feature-blindspot trigger).
        "yono_actions_30d": ["upi", "balance_check", "upi", "upi", "balance_check", "upi"],
        "features_ever_used": ["upi", "balance_check"],
        "external_recurring": [
            {"payee": "BESCOM ELECTRICITY", "via": "PhonePe", "amount": 1180,
             "cadence": "monthly", "feature": "bill_pay"},
        ],
        "ledger": led,
    }


def persona_subscription_saver(rng: random.Random) -> dict:
    """Recurring OTT/fitness/storage debits, some unused; saving toward a goal."""
    pid = "p5_subscription_saver"
    led = Ledger(pid, opening_balance=20000.0)
    for m in range(4, 0, -1):
        led.add(m * 30 + 5, 55000.0, "WIPRO LTD SALARY", "salary", "NACH")
        led.add(m * 30 + 4, -649.0, "NETFLIX", "merchant", "UPI")
        led.add(m * 30 + 4, -1300.0, "CULT FIT", "merchant", "UPI")
        led.add(m * 30 + 3, -130.0, "GOOGLE ONE", "merchant", "card")
        led.add(m * 30 + 1, -30000.0, "RENT PRESTIGE APTS", "transfer", "IMPS")
    _spends(led, rng, start_days=120, end_days=2, n=38, lo=120, hi=2200)
    return {
        "persona_id": pid,
        "name": "Priya Nair",
        "headline": "Subscription Saver",
        "flow": "S",
        "blurb": "Several monthly subscriptions — some unused; saving toward a goal.",
        "language_pref": "en",
        "monthly_income": 55000,
        "subscriptions": [
            {"sub_id": "s1", "name": "NETFLIX", "category": "OTT", "amount": 649,
             "cadence": "monthly", "via": "UPI_AUTOPAY", "used_last_30d": True,
             "next_charge_in_days": 12},
            {"sub_id": "s2", "name": "CULT FIT", "category": "FITNESS", "amount": 1300,
             "cadence": "monthly", "via": "UPI_AUTOPAY", "used_last_30d": False,
             "next_charge_in_days": 3},
            {"sub_id": "s3", "name": "GOOGLE ONE", "category": "STORAGE", "amount": 130,
             "cadence": "monthly", "via": "card", "used_last_30d": False,
             "next_charge_in_days": 14},
        ],
        "goals": [
            {"goal_id": "g1", "label": "Buy a bike", "target_amount": 120000,
             "target_date": "2027-06-01", "saved_so_far": 38000},
        ],
        "ledger": led,
    }


def build() -> dict:
    rng = random.Random(SEED)
    builders = [
        persona_idle_saver,
        persona_premium_leaker,
        persona_new_earner,
        persona_explorer,
        persona_subscription_saver,
    ]
    personas_meta: list[dict] = []
    transactions: dict[str, list[dict]] = {}

    for make in builders:
        p = make(rng)
        led: Ledger = p.pop("ledger")
        rows = led.rows()
        transactions[p["persona_id"]] = rows
        p["current_balance"] = rows[-1]["balance_after"] if rows else 0.0
        p["transaction_count"] = len(rows)
        personas_meta.append(p)

    return {
        "generated_at": REF.isoformat(),
        "seed": SEED,
        "personas": personas_meta,
        "transactions": transactions,
    }


def main() -> None:
    dataset = build()
    OUT_PATH.write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(len(v) for v in dataset["transactions"].values())
    print(f"Wrote {OUT_PATH} - {len(dataset['personas'])} personas, {total} transactions.")
    for p in dataset["personas"]:
        print(
            f"  [{p['flow']}] {p['persona_id']:<18} {p['name']:<14} "
            f"balance=Rs.{p['current_balance']:,.0f}  txns={p['transaction_count']}"
        )


if __name__ == "__main__":
    main()
