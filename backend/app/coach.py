"""
coach.py — the "brain" that connects everything for one question.

The flow for every question (this is your system architecture in code):

    user question
         |
    1. guardrails.check_message()   -> blocked? return the safe message
         |
    2. retriever.search()           -> find the top trusted passages
         |
    3. llm.grounded_answer()        -> AI writes a plain-English answer citing them
       (or offline mode: return the passages themselves)
         |
    4. add citations + disclaimer   -> send back to the user
"""

from __future__ import annotations

from . import config, llm
from .guardrails import DISCLAIMER, check_message
from .retriever import Retriever

_retriever = Retriever.from_file()


def _format_sources(results) -> str:
    return "\n".join(f"[{i}] {p.title} ({p.source}): {p.text}" for i, (p, _) in enumerate(results, 1))


def ask(question: str) -> dict:
    # Step 1: safety check
    guard = check_message(question)
    if not guard.allowed:
        return {"answer": guard.message, "blocked": True, "category": guard.category,
                "citations": [], "disclaimer": DISCLAIMER, "mode": "guardrail"}

    # Step 2: retrieve trusted passages
    results = _retriever.search(question, top_k=3)
    citations = [{"n": i, "title": p.title, "source": p.source, "url": p.url, "score": s}
                 for i, (p, s) in enumerate(results, 1)]

    if not results:
        return {"answer": "I don't have a trusted source on that yet. Try rephrasing, or ask "
                          "about saving, credit, budgeting, debt, or investing basics.",
                "blocked": False, "category": "no_sources", "citations": [],
                "disclaimer": DISCLAIMER, "mode": "no_sources"}

    # Step 3: generate the answer
    if config.OFFLINE_MODE:
        top = results[0][0]
        answer = f"{top.text} [1]"
        mode = "offline"
    else:
        answer = llm.grounded_answer(question, _format_sources(results))
        mode = "llm"

    # Step 4: package it up
    return {"answer": answer, "blocked": False, "category": "ok", "citations": citations,
            "disclaimer": DISCLAIMER, "mode": mode}
