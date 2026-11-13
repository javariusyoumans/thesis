"""
calculators.py — the "math engine" of Legacy AI.

WHY THIS FILE EXISTS
--------------------
AI language models are great at explaining ideas but can make arithmetic
mistakes. Money math has to be exact, so Legacy AI NEVER lets the AI do the
math. Every number a user sees comes from one of these plain Python functions,
which we can test and prove correct (see backend/tests/test_calculators.py).

Every function here is "pure": same inputs -> same outputs, no internet,
no database. That makes them easy to test and easy to trust.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# 1. Compound growth: "If I invest $X a month, what will it be worth?"
# ---------------------------------------------------------------------------
def compound_growth(
    starting_amount: float,
    monthly_contribution: float,
    annual_return_rate: float,
    years: int,
) -> dict:
    """
    Grow money month by month.

    annual_return_rate is a decimal: 0.07 means 7% per year.
    Returns the final balance, how much you put in, how much was growth,
    and a year-by-year list (useful for drawing a chart later).
    """
    if years < 0 or starting_amount < 0 or monthly_contribution < 0:
        raise ValueError("Amounts and years cannot be negative.")

    monthly_rate = annual_return_rate / 12
    balance = starting_amount
    total_contributed = starting_amount
    yearly_balances = []

    for month in range(1, years * 12 + 1):
        balance = balance * (1 + monthly_rate)   # interest/growth for the month
        balance += monthly_contribution          # then add this month's deposit
        total_contributed += monthly_contribution
        if month % 12 == 0:                      # end of each year, save a snapshot
            yearly_balances.append({"year": month // 12, "balance": round(balance, 2)})

    return {
        "final_balance": round(balance, 2),
        "total_contributed": round(total_contributed, 2),
        "total_growth": round(balance - total_contributed, 2),
        "yearly_balances": yearly_balances,
    }


# ---------------------------------------------------------------------------
# 2. Savings goal: "How long until I reach $1,000?"
# ---------------------------------------------------------------------------
def months_to_goal(
    goal_amount: float,
    current_savings: float,
    monthly_saving: float,
    annual_interest_rate: float = 0.0,
    max_months: int = 1200,
) -> int | None:
    """
    Count how many months it takes to reach a savings goal.
    Returns 0 if you're already there, or None if you'll never get there
    (for example, saving $0 a month with no interest).
    """
    if current_savings >= goal_amount:
        return 0
    if monthly_saving <= 0 and annual_interest_rate <= 0:
        return None

    monthly_rate = annual_interest_rate / 12
    balance = current_savings
    for month in range(1, max_months + 1):
        balance = balance * (1 + monthly_rate) + monthly_saving
        if balance >= goal_amount:
            return month
    return None


# ---------------------------------------------------------------------------
# 3. Emergency fund plan
# ---------------------------------------------------------------------------
def emergency_fund_plan(monthly_expenses: float, current_savings: float) -> dict:
    """
    A common, conservative approach: hit a $1,000 "starter" cushion first,
    then build toward 3 months of expenses, then 6 months.
    These milestones are educational rules of thumb, not personal advice.
    """
    if monthly_expenses <= 0:
        raise ValueError("Monthly expenses must be greater than zero.")

    milestones = [
        ("Starter cushion", 1000.0),
        ("3 months of expenses", monthly_expenses * 3),
        ("6 months of expenses", monthly_expenses * 6),
    ]
    plan = []
    for name, target in milestones:
        plan.append({
            "milestone": name,
            "target": round(target, 2),
            "remaining": round(max(target - current_savings, 0), 2),
            "reached": current_savings >= target,
        })
    return {"monthly_expenses": monthly_expenses, "current_savings": current_savings, "milestones": plan}


# ---------------------------------------------------------------------------
# 4. Credit utilization: a big part of a credit score
# ---------------------------------------------------------------------------
def credit_utilization(balances: list[float], limits: list[float]) -> dict:
    """
    Utilization = total card balances / total credit limits.
    Lower is generally better. Common guidance: under 30%, and under 10% is
    excellent. Returns the percentage plus a plain-English band.
    """
    if len(balances) != len(limits):
        raise ValueError("Each card needs both a balance and a limit.")
    total_limit = sum(limits)
    if total_limit <= 0:
        raise ValueError("Total credit limit must be greater than zero.")

    pct = sum(balances) / total_limit * 100
    if pct < 10:
        band = "excellent"
    elif pct < 30:
        band = "good"
    elif pct < 50:
        band = "fair"
    else:
        band = "high"
    return {
        "utilization_percent": round(pct, 1),
        "band": band,
        "amount_to_pay_to_reach_30_percent": round(max(sum(balances) - 0.30 * total_limit, 0), 2),
    }


# ---------------------------------------------------------------------------
# 5. Debt payoff: avalanche vs. snowball
# ---------------------------------------------------------------------------
@dataclass
class Debt:
    name: str
    balance: float
    annual_rate: float       # 0.24 = 24% APR
    minimum_payment: float


@dataclass
class PayoffResult:
    method: str
    months: int
    total_interest: float
    payoff_order: list[str] = field(default_factory=list)


def debt_payoff(debts: list[Debt], monthly_budget: float, method: str = "avalanche",
                max_months: int = 600) -> PayoffResult:
    """
    Simulate paying off several debts month by month.

    - "avalanche": put extra money on the HIGHEST interest rate first
      (saves the most money).
    - "snowball": put extra money on the SMALLEST balance first
      (quick wins that help people stay motivated).

    monthly_budget is the total you can pay across all debts each month.
    """
    if method not in ("avalanche", "snowball"):
        raise ValueError("method must be 'avalanche' or 'snowball'")
    minimums = sum(d.minimum_payment for d in debts)
    if monthly_budget < minimums:
        raise ValueError(f"Budget must cover all minimum payments (${minimums:.2f}).")

    # Copy so we don't change the caller's data
    remaining = {d.name: d.balance for d in debts}
    info = {d.name: d for d in debts}
    total_interest = 0.0
    order: list[str] = []

    for month in range(1, max_months + 1):
        # 1) Add this month's interest to every unpaid debt
        for name, bal in remaining.items():
            if bal > 0:
                interest = bal * info[name].annual_rate / 12
                remaining[name] = bal + interest
                total_interest += interest

        # 2) Pay minimums first
        money_left = monthly_budget
        for name in remaining:
            if remaining[name] > 0:
                pay = min(info[name].minimum_payment, remaining[name])
                remaining[name] -= pay
                money_left -= pay

        # 3) Send extra money to the target debt(s) in priority order
        unpaid = [n for n in remaining if remaining[n] > 0]
        if method == "avalanche":
            unpaid.sort(key=lambda n: info[n].annual_rate, reverse=True)
        else:
            unpaid.sort(key=lambda n: remaining[n])
        for name in unpaid:
            if money_left <= 0:
                break
            pay = min(money_left, remaining[name])
            remaining[name] -= pay
            money_left -= pay

        # 4) Record debts that just hit zero
        for name in remaining:
            if remaining[name] <= 0.005 and name not in order:
                remaining[name] = 0
                order.append(name)

        if all(b == 0 for b in remaining.values()):
            return PayoffResult(method, month, round(total_interest, 2), order)

    raise ValueError("Debts are not paid off within the time limit; budget may be too low.")
