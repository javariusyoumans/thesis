"""Tests prove the math is right. Run them with: pytest"""
import pytest

from app import calculators as c


def test_compound_growth_no_interest_is_just_deposits():
    r = c.compound_growth(100, 50, 0.0, 2)
    assert r["final_balance"] == 100 + 50 * 24
    assert r["total_growth"] == 0


def test_compound_growth_matches_formula():
    # $1,000 at 12%/yr compounded monthly for 1 year = 1000 * 1.01^12
    r = c.compound_growth(1000, 0, 0.12, 1)
    assert r["final_balance"] == pytest.approx(1000 * 1.01 ** 12, abs=0.01)


def test_months_to_goal():
    assert c.months_to_goal(1000, 100, 100) == 9      # 100 + 9*100 = 1000
    assert c.months_to_goal(500, 600, 0) == 0         # already there
    assert c.months_to_goal(1000, 0, 0) is None       # never


def test_emergency_fund_plan():
    plan = c.emergency_fund_plan(1200, 1500)["milestones"]
    assert plan[0]["reached"] is True                 # $1,000 starter
    assert plan[1]["target"] == 3600 and plan[1]["remaining"] == 2100


def test_credit_utilization_bands():
    assert c.credit_utilization([300], [1000])["band"] == "fair"      # exactly 30%
    assert c.credit_utilization([50], [1000])["band"] == "excellent"
    r = c.credit_utilization([600], [1000])
    assert r["band"] == "high" and r["amount_to_pay_to_reach_30_percent"] == 300


def test_credit_utilization_rejects_bad_input():
    with pytest.raises(ValueError):
        c.credit_utilization([100], [0])


DEBTS = [
    c.Debt("Store card", 500, 0.28, 25),
    c.Debt("Visa", 2000, 0.22, 50),
    c.Debt("Car loan", 4000, 0.07, 120),
]


def test_avalanche_never_costs_more_than_snowball():
    av = c.debt_payoff(DEBTS, 400, "avalanche")
    sn = c.debt_payoff(DEBTS, 400, "snowball")
    assert av.total_interest <= sn.total_interest
    assert sn.payoff_order[0] == "Store card"         # smallest balance first


def test_budget_must_cover_minimums():
    with pytest.raises(ValueError):
        c.debt_payoff(DEBTS, 100)
