"""
actions.py — the "approve-first" action system.

WHY THIS FILE EXISTS
--------------------
Legacy AI can SUGGEST actions ("move $25 to savings every Friday"), but it can
never DO anything on its own. Every action goes through three states:

    proposed  -->  approved  -->  completed (simulated)
        |
        +-->  rejected

Nothing moves real money. In the pilot, "completed" just means the action is
logged as if it happened. This keeps the project legal and safe, and it lets
you measure something interesting for Sub-question 3: how often users approve
what the coach suggests, and why.

Storage is in memory for now (it resets when the server restarts).
Later this becomes a database table.
"""

from __future__ import annotations

import itertools
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ActionType(str, Enum):
    SET_SAVINGS_GOAL = "set_savings_goal"
    SCHEDULE_TRANSFER = "schedule_transfer"          # simulated only
    CREDIT_REPORT_REMINDER = "credit_report_reminder"
    SPENDING_ALERT = "spending_alert"


class ActionStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Action:
    id: int
    user_id: str
    type: ActionType
    description: str
    amount: float | None = None
    reason: str = ""                        # the "why": shown to the user (explainability)
    status: ActionStatus = ActionStatus.PROPOSED
    history: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class ActionStore:
    def __init__(self):
        self._actions: dict[int, Action] = {}
        self._ids = itertools.count(1)

    def propose(self, user_id: str, type: ActionType, description: str,
                amount: float | None = None, reason: str = "") -> Action:
        if amount is not None and amount < 0:
            raise ValueError("Amount cannot be negative.")
        action = Action(next(self._ids), user_id, type, description, amount, reason)
        action.history.append({"status": action.status, "at": _now()})
        self._actions[action.id] = action
        return action

    def _move(self, action_id: int, allowed_from: ActionStatus, to: ActionStatus) -> Action:
        action = self._actions.get(action_id)
        if action is None:
            raise KeyError(f"No action with id {action_id}")
        if action.status != allowed_from:
            raise ValueError(f"Can't go from '{action.status.value}' to '{to.value}'.")
        action.status = to
        action.history.append({"status": to, "at": _now()})
        return action

    def approve(self, action_id: int) -> Action:
        # Approval immediately "executes" in simulation mode.
        self._move(action_id, ActionStatus.PROPOSED, ActionStatus.APPROVED)
        return self._move(action_id, ActionStatus.APPROVED, ActionStatus.COMPLETED)

    def reject(self, action_id: int) -> Action:
        return self._move(action_id, ActionStatus.PROPOSED, ActionStatus.REJECTED)

    def list_for(self, user_id: str) -> list[Action]:
        return [a for a in self._actions.values() if a.user_id == user_id]
