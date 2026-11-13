"""End-to-end tests: call the API the same way a website would."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_coach_returns_cited_answer():
    r = client.post("/coach/ask", json={"question": "What is credit utilization?"}).json()
    assert not r["blocked"]
    assert r["citations"][0]["title"] == "Credit utilization"


def test_coach_blocks_stock_picks():
    r = client.post("/coach/ask", json={"question": "Which stock should I buy?"}).json()
    assert r["blocked"] and r["category"] == "specific_security"


def test_calculator_endpoint_validates_input():
    bad = client.post("/calc/compound-growth", json={"starting_amount": -5, "monthly_contribution": 1,
                                                      "annual_return_rate": 0.05, "years": 1})
    assert bad.status_code == 422


def test_action_lifecycle_over_api():
    a = client.post("/actions/propose", json={"user_id": "s1", "type": "set_savings_goal",
                                              "description": "Save $1,000 starter fund"}).json()
    done = client.post(f"/actions/{a['id']}/approve").json()
    assert done["status"] == "completed"
    assert client.post(f"/actions/{a['id']}/approve").status_code == 409
