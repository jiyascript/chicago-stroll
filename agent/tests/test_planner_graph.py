"""Integration tests for the Chicago Stroll planner graph."""

from datetime import date

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from app.state import PlannerState


def fake_parse_request(state: PlannerState) -> dict:
    """Return a deterministic parsed request."""

    return {
        "trip_request": {
            "date": None,
            "start_time": "11:00",
            "end_time": "20:00",
            "start_location": "Hyde Park",
            "end_location": "Union Station",
            "group_type": "family",
            "group_size": None,
            "interests": ["architecture"],
            "dietary_preferences": ["vegetarian"],
            "budget": 150.0,
            "pace": None,
            "walking_tolerance": "limited",
            "preferred_neighborhoods": [],
            "excluded_neighborhoods": [],
            "must_include": [],
            "must_avoid": [],
            "indoor_outdoor_preference": None,
        }
    }


def fake_update_request(state: PlannerState) -> dict:
    """Add the missing date while preserving existing request data."""

    updated = dict(state["trip_request"])
    updated["date"] = date(2026, 8, 8)

    return {
        "trip_request": updated,
        "clarification_question": None,
        "ready_for_research": False,
    }


def fake_check_completeness(state: PlannerState) -> dict:
    """Check only the required planning fields."""

    request = state["trip_request"]

    required_fields = (
        "date",
        "start_time",
        "end_time",
        "start_location",
    )

    missing = [
        field
        for field in required_fields
        if request.get(field) is None
    ]

    return {
        "missing_fields": missing,
    }


def fake_create_clarification(state: PlannerState) -> dict:
    """Return deterministic clarification text."""

    return {
        "clarification_question": "What date are you planning for?",
        "ready_for_research": False,
    }


def fake_ready_for_research(state: PlannerState) -> dict:
    """Mark the request ready."""

    return {
        "clarification_question": None,
        "ready_for_research": True,
    }


def route_initial_request(state: PlannerState) -> str:
    if state.get("trip_request") is None:
        return "parse_request"

    return "update_request"


def route_after_completeness(state: PlannerState) -> str:
    if state.get("missing_fields"):
        return "create_clarification"

    return "ready_for_research"


def create_test_graph():
    """Build a deterministic planner graph for testing."""

    builder = StateGraph(PlannerState)

    builder.add_node("parse_request", fake_parse_request)
    builder.add_node("update_request", fake_update_request)
    builder.add_node("check_completeness", fake_check_completeness)
    builder.add_node("create_clarification", fake_create_clarification)
    builder.add_node("ready_for_research", fake_ready_for_research)

    builder.add_conditional_edges(
        START,
        route_initial_request,
    )

    builder.add_edge(
        "parse_request",
        "check_completeness",
    )

    builder.add_edge(
        "update_request",
        "check_completeness",
    )

    builder.add_conditional_edges(
        "check_completeness",
        route_after_completeness,
    )

    builder.add_edge(
        "create_clarification",
        END,
    )

    builder.add_edge(
        "ready_for_research",
        END,
    )

    return builder.compile(
        checkpointer=InMemorySaver(),
    )
def test_incomplete_request_routes_to_clarification() -> None:
    graph = create_test_graph()

    config = {
        "configurable": {
            "thread_id": "test-incomplete",
        }
    }

    result = graph.invoke(
        {
            "user_message": "Plan something in Chicago.",
        },
        config=config,
    )

    assert result["missing_fields"] == ["date"]
    assert result["clarification_question"] == (
        "What date are you planning for?"
    )
    assert result["ready_for_research"] is False


def test_complete_request_routes_to_research() -> None:
    graph = create_test_graph()

    config = {
        "configurable": {
            "thread_id": "test-complete",
        }
    }

    result = graph.invoke(
        {
            "user_message": "Plan something in Chicago.",
            "trip_request": {
                "date": date(2026, 8, 8),
                "start_time": "11:00",
                "end_time": "20:00",
                "start_location": "Hyde Park",
            },
        },
        config=config,
    )

    assert result["missing_fields"] == []
    assert result["ready_for_research"] is True
    assert result["clarification_question"] is None


def test_followup_updates_persisted_request() -> None:
    graph = create_test_graph()

    config = {
        "configurable": {
            "thread_id": "test-multi-turn",
        }
    }

    first_result = graph.invoke(
        {
            "user_message": "My parents are visiting Chicago.",
        },
        config=config,
    )

    assert first_result["missing_fields"] == ["date"]

    second_result = graph.invoke(
        {
            "user_message": "August 8, 2026.",
        },
        config=config,
    )

    assert second_result["trip_request"]["date"] == date(2026, 8, 8)
    assert second_result["trip_request"]["start_location"] == "Hyde Park"
    assert second_result["missing_fields"] == []
    assert second_result["ready_for_research"] is True