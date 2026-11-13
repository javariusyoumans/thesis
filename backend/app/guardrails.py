"""
guardrails.py — the "safety checker" that runs BEFORE the AI answers.

WHY THIS FILE EXISTS
--------------------
Legacy AI is an educational coach, not a licensed financial advisor. Some
questions it should not answer directly (like "which stock should I buy?"),
and some messages need a human resource instead of a money answer.
This file catches those cases with simple, predictable rules so the behavior
is easy to explain to your committee and easy to test.

This is version 1 (keyword rules). Later you could add an AI-based classifier
and compare the two — that comparison could even be part of your results.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class GuardrailResult:
    allowed: bool          # True = safe to send to the coach
    category: str          # which rule matched ("ok" if none)
    message: str = ""      # what to tell the user if not allowed


# Each rule: (category, list of regex patterns, response message)
# Patterns are lowercase and use \b for whole-word matching.
_RULES: list[tuple[str, list[str], str]] = [
    (
        "crisis",
        [r"\bkill myself\b", r"\bsuicid", r"\bend my life\b", r"\bself[- ]harm\b"],
        "It sounds like you're going through something really hard. You don't have to "
        "handle it alone. In the U.S., you can call or text 988 to reach the 988 Suicide "
        "& Crisis Lifeline any time. Money stress is real, and once you're safe I'm here "
        "to help you work through it step by step.",
    ),
    (
        "sensitive_data",
        [r"\b\d{3}-\d{2}-\d{4}\b",             # SSN format
         r"\b(?:\d[ -]?){13,16}\b"],           # card-number-like digit runs
        "Please don't share Social Security numbers, card numbers, or account numbers "
        "here. I don't need them to help you, and keeping them private protects you.",
    ),
    (
        "specific_security",
        [r"\bwhich (stock|crypto|coin)s?\b", r"\bshould i (buy|sell)\b",
         r"\bbest (stock|crypto|coin)s?\b", r"\bwhat (stock|crypto|coin)s? should\b"],
        "I can't tell you to buy or sell a specific stock or coin. That's personalized "
        "investment advice, which requires a licensed professional. What I can do is "
        "explain how stocks, index funds, and diversification work so you can make that "
        "decision with confidence. Want to start there?",
    ),
    (
        "illegal",
        [r"\b(evade|avoid paying) (my )?taxes\b", r"\blaunder", r"\bfake (pay ?stub|w-?2|id)\b",
         r"\bcredit (repair )?hack\b.*\b(ssn|cpn)\b", r"\bcpn\b"],
        "I can't help with that because it could break the law and put you at serious "
        "risk. I'm happy to help with legal ways to lower taxes or rebuild credit.",
    ),
]


def check_message(text: str) -> GuardrailResult:
    """Run every rule in order. The first match wins (crisis is checked first)."""
    lowered = text.lower()
    for category, patterns, message in _RULES:
        if any(re.search(p, lowered) for p in patterns):
            return GuardrailResult(allowed=False, category=category, message=message)
    return GuardrailResult(allowed=True, category="ok")


# Shown under every coach answer.
DISCLAIMER = (
    "Legacy AI provides financial education, not personalized investment, legal, or "
    "tax advice. Check important decisions with a qualified professional."
)
