# Legacy AI
# Javarius Authur Youmans

**An explainable, goal-driven AI financial literacy coach.**
Senior capstone project by Javarius Youmans, Department of Mathematics and Computer Science, Claflin University.

Legacy AI helps students and young adults **learn** how money works, **plan** toward real goals (emergency fund, credit, debt payoff, investing), and **act** on those plans. The system can only act after the user approves.

> ⚠️ Legacy AI is an educational research prototype. It does not give personalized investment, legal, or tax advice, and it never moves real money.

## How it works

```
 User question ──► Guardrails ──► Retriever (trusted sources) ──► AI writes answer with citations
                       │
                       └─► blocked? safe response (e.g., no stock picks, crisis resources)

 Planning ──► Calculators (exact, tested math — the AI never does the arithmetic)

 Actions ──► proposed ──► user approves ──► completed (simulated)
                     └──► user rejects
```

| Layer | File | What it does |
|---|---|---|
| Learn | `backend/app/coach.py`, `retriever.py`, `llm.py` | Answers questions using vetted public sources (CFPB, FDIC, IRS, SEC) and cites them |
| Safety | `backend/app/guardrails.py` | Blocks stock picks, sensitive data, illegal requests; routes crisis messages to 988 |
| Plan | `backend/app/calculators.py` | Compound growth, savings goals, emergency fund, credit utilization, avalanche/snowball debt payoff |
| Act | `backend/app/actions.py` | Approve-first action workflow with a full history log |
| API | `backend/app/main.py` | FastAPI endpoints; interactive docs at `/docs` |

## Quick start (VS Code)

New to this? Read **[docs/WALKTHROUGH.md](docs/WALKTHROUGH.md)** first. It explains every step.

```bash
python -m venv .venv
# Windows:   .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest                                   # run the tests
uvicorn app.main:app --reload --app-dir backend
```
Then open http://127.0.0.1:8000/docs.

To use a real AI model, copy `.env.example` to `.env` and add your API key. Without a key, the app runs in **offline mode** and returns the top trusted source directly.

## Roadmap
- [x] Backend skeleton: guardrails, retrieval, calculators, approve-first actions, tests
- [ ] Expand and verify the knowledge base (every source re-checked against its URL)
- [ ] Evaluation harness: grounded vs. baseline AI on a question benchmark (Sub-question 1)
- [ ] Database (users, goals, action logs) and simulated transactions
- [ ] Web front end (React) with Claflin branding
- [ ] Pilot study instrumentation: P-Fin 8 quiz, CFPB Financial Well-Being Scale, usage logs
