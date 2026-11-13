"""
schemas.py — describes the SHAPE of data coming into the API.

Pydantic checks every request automatically. If someone sends
{"years": "banana"}, FastAPI rejects it with a clear error before your code
ever runs. These classes also power the free interactive docs at /docs.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .actions import ActionType


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000, examples=["How do I start building credit?"])


class CompoundRequest(BaseModel):
    starting_amount: float = Field(ge=0, examples=[0])
    monthly_contribution: float = Field(ge=0, examples=[50])
    annual_return_rate: float = Field(ge=-1, le=1, examples=[0.07])
    years: int = Field(ge=0, le=80, examples=[40])


class GoalRequest(BaseModel):
    goal_amount: float = Field(gt=0, examples=[1000])
    current_savings: float = Field(ge=0, examples=[100])
    monthly_saving: float = Field(ge=0, examples=[75])
    annual_interest_rate: float = Field(default=0.0, ge=0, le=1, examples=[0.04])


class EmergencyFundRequest(BaseModel):
    monthly_expenses: float = Field(gt=0, examples=[1200])
    current_savings: float = Field(ge=0, examples=[250])


class UtilizationRequest(BaseModel):
    balances: list[float] = Field(examples=[[300, 150]])
    limits: list[float] = Field(examples=[[1000, 500]])


class DebtIn(BaseModel):
    name: str
    balance: float = Field(gt=0)
    annual_rate: float = Field(ge=0, le=1)
    minimum_payment: float = Field(ge=0)


class DebtPayoffRequest(BaseModel):
    debts: list[DebtIn]
    monthly_budget: float = Field(gt=0)
    method: Literal["avalanche", "snowball"] = "avalanche"


class ProposeActionRequest(BaseModel):
    user_id: str = Field(examples=["student-001"])
    type: ActionType
    description: str = Field(examples=["Move $25 to savings every Friday"])
    amount: float | None = Field(default=None, ge=0, examples=[25])
    reason: str = Field(default="", examples=["You're 3 months from your $1,000 starter fund."])
