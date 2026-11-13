"""
main.py — the front door of the backend (the API).

An API is a set of URLs other programs can call. Your future website or phone
app will send requests here, and this file routes each one to the right code.

Run it (from the project root, with your virtual environment active):
    uvicorn app.main:app --reload --app-dir backend
Then open http://127.0.0.1:8000/docs to click and test every endpoint.
"""

from dataclasses import asdict

from fastapi import FastAPI, HTTPException

from . import calculators, coach, config
from .actions import ActionStore
from .schemas import (AskRequest, CompoundRequest, DebtPayoffRequest, EmergencyFundRequest,
                      GoalRequest, ProposeActionRequest, UtilizationRequest)

app = FastAPI(
    title="Legacy AI",
    description="An explainable, goal-driven AI financial literacy coach (Claflin University capstone).",
    version="0.1.0",
)
actions = ActionStore()


@app.get("/health")
def health():
    """Quick check that the server is running."""
    return {"status": "ok", "offline_mode": config.OFFLINE_MODE}


# ---------- Learn: the coach ----------
@app.post("/coach/ask")
def ask(req: AskRequest):
    return coach.ask(req.question)


# ---------- Plan: calculators ----------
@app.post("/calc/compound-growth")
def compound(req: CompoundRequest):
    return calculators.compound_growth(**req.model_dump())


@app.post("/calc/months-to-goal")
def goal(req: GoalRequest):
    months = calculators.months_to_goal(**req.model_dump())
    return {"months": months, "reachable": months is not None}


@app.post("/calc/emergency-fund")
def emergency(req: EmergencyFundRequest):
    return calculators.emergency_fund_plan(**req.model_dump())


@app.post("/calc/credit-utilization")
def utilization(req: UtilizationRequest):
    try:
        return calculators.credit_utilization(req.balances, req.limits)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/calc/debt-payoff")
def debt(req: DebtPayoffRequest):
    debts = [calculators.Debt(**d.model_dump()) for d in req.debts]
    try:
        return asdict(calculators.debt_payoff(debts, req.monthly_budget, req.method))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- Act: approve-first actions ----------
@app.post("/actions/propose")
def propose(req: ProposeActionRequest):
    return actions.propose(**req.model_dump()).to_dict()


@app.post("/actions/{action_id}/approve")
def approve(action_id: int):
    try:
        return actions.approve(action_id).to_dict()
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.post("/actions/{action_id}/reject")
def reject(action_id: int):
    try:
        return actions.reject(action_id).to_dict()
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.get("/actions/{user_id}")
def list_actions(user_id: str):
    return [a.to_dict() for a in actions.list_for(user_id)]
