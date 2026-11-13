"""
llm.py — the ONLY file that talks to the AI model.

Keeping all AI calls in one place means:
  - you can swap providers later by editing just this file, and
  - your evaluation can compare "with sources" vs "without sources" (your
    Sub-question 1) by calling these two functions.
"""

from __future__ import annotations

from . import config

SYSTEM_PROMPT = """You are Legacy AI, a friendly financial literacy coach for college students
and young adults. Rules you must follow:
1. Answer ONLY using the numbered sources provided. Cite them like [1] or [2].
2. If the sources don't cover the question, say so plainly and suggest a trusted place to look.
3. Never recommend buying or selling a specific stock, fund, or coin.
4. Do not do arithmetic yourself. If numbers are needed, say which calculator in the app to use.
5. Use plain, encouraging language. Define any financial term the first time you use it.
6. Keep answers under 200 words."""


def _call_model(system: str, user: str) -> str:
    # Imported here so the app still runs if the package isn't installed yet
    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=config.LLM_MODEL,
        max_tokens=600,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


def grounded_answer(question: str, sources_block: str) -> str:
    """The real Legacy AI answer: model + retrieved sources + rules."""
    user = f"Sources:\n{sources_block}\n\nQuestion: {question}"
    return _call_model(SYSTEM_PROMPT, user)


def baseline_answer(question: str) -> str:
    """The comparison 'plain chatbot' answer for your evaluation: no sources, no rules."""
    return _call_model("You are a helpful assistant.", question)
