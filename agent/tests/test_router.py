from types import SimpleNamespace
from app.graph.router import (
    route_after_critic,
    route_after_recovery,
    route_planner_agent,
)
def test_tool_call_routes_to_tools():
    s={"messages":[SimpleNamespace(tool_calls=[{"name":"SearchPlaces"}])],"planner_steps":1,"tool_call_count":0}
    assert route_planner_agent(s)=="planner_tools"
def test_repair_budget_is_enforced():
    s={"recovery_decision":{"action":"repair"},"repair_count":2,"replan_count":0}
    assert route_after_recovery(s)=="best_effort"
def test_replan_budget_is_enforced():
    s={"recovery_decision":{"action":"search_again"},"repair_count":0,"replan_count":2}
    assert route_after_recovery(s)=="ask_user"
def test_valid_critique_finishes():
    state = {
        "critique_result": {
            "is_valid": True,
        }
    }

    assert route_after_critic(state) == "finished"


def test_invalid_critique_routes_to_recovery():
    state = {
        "critique_result": {
            "is_valid": False,
        }
    }

    assert route_after_critic(state) == "recovery"


def test_recovery_can_choose_repair():
    state = {
        "recovery_decision": {"action": "repair"},
        "repair_count": 0,
        "replan_count": 0,
    }

    assert route_after_recovery(state) == "repair"


def test_recovery_can_choose_replan():
    state = {
        "recovery_decision": {"action": "replan"},
        "repair_count": 0,
        "replan_count": 0,
    }

    assert route_after_recovery(state) == "replan"


def test_search_again_routes_to_replan():
    state = {
        "recovery_decision": {"action": "search_again"},
        "repair_count": 0,
        "replan_count": 0,
    }

    assert route_after_recovery(state) == "replan"


def test_recovery_can_ask_user():
    state = {
        "recovery_decision": {"action": "ask_user"},
        "repair_count": 0,
        "replan_count": 0,
    }

    assert route_after_recovery(state) == "ask_user"


def test_recovery_can_choose_best_effort():
    state = {
        "recovery_decision": {"action": "best_effort"},
        "repair_count": 0,
        "replan_count": 0,
    }

    assert route_after_recovery(state) == "best_effort"