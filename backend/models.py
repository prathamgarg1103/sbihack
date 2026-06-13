"""Shared Pydantic models for the Saarthi backend."""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TriggerType(str, Enum):
    IDLE_BALANCE = "idle_balance"
    PREMIUM_LEAK = "premium_leak"
    SALARY_JUMP = "salary_jump"
    CONTEXTUAL_SPEND = "contextual_spend"


class PayeeCategory(str, Enum):
    PREMIUM = "premium"
    SALARY = "salary"
    MERCHANT = "merchant"
    TRANSFER = "transfer"
    BILL = "bill"


class AdoptionMoment(BaseModel):
    """A detected, machine-found opportunity to (maybe) nudge the user.

    This is the perceive→detect output. The agent core (M5) decides whether it
    is actually worth surfacing; the trigger engine only finds candidates.
    """

    trigger_type: TriggerType
    persona_id: str
    title: str
    summary: str
    severity: str = Field(description="low | medium | high")
    suggested_category: str = Field(
        description="fixed_deposit | insurance_compare | micro_cover",
    )
    evidence: dict[str, Any] = Field(default_factory=dict)
    evidence_txn_ids: list[str] = Field(default_factory=list)
