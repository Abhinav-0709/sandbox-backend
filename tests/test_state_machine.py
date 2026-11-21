import pytest
from app.services.session_service import VALID_TRANSITIONS


def test_state_machine_valid_transitions():
    assert "READY" in VALID_TRANSITIONS["CREATED"]
    assert "RUNNING" in VALID_TRANSITIONS["READY"]
    assert "PAUSED" in VALID_TRANSITIONS["RUNNING"]
    assert "COMPLETED" in VALID_TRANSITIONS["RUNNING"]
    assert "RUNNING" in VALID_TRANSITIONS["PAUSED"]
    assert "COMPLETED" in VALID_TRANSITIONS["PAUSED"]
    assert len(VALID_TRANSITIONS["COMPLETED"]) == 0
    assert len(VALID_TRANSITIONS["TERMINATED"]) == 0


def test_terminal_states_cannot_transition():
    for terminal in ["COMPLETED", "TERMINATED"]:
        assert VALID_TRANSITIONS[terminal] == []
