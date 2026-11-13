import pytest

from app.actions import ActionStatus, ActionStore, ActionType


def test_approve_flow():
    store = ActionStore()
    a = store.propose("u1", ActionType.SCHEDULE_TRANSFER, "Save $25 weekly", 25)
    assert a.status == ActionStatus.PROPOSED
    store.approve(a.id)
    assert a.status == ActionStatus.COMPLETED
    assert [h["status"] for h in a.history] == ["proposed", "approved", "completed"]


def test_cannot_approve_rejected_action():
    store = ActionStore()
    a = store.propose("u1", ActionType.SET_SAVINGS_GOAL, "Save $1,000")
    store.reject(a.id)
    with pytest.raises(ValueError):
        store.approve(a.id)
