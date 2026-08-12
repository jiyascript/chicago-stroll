"""Tests for the planner LangGraph node."""

from unittest.mock import patch

from app.nodes.planner import planner_node
from app.schemas import DraftItinerary


@patch("app.nodes.planner.generate_itinerary")
def test_planner_node_adds_draft_itinerary(
    mock_generate_itinerary,
) -> None:
    """The planner node should add a draft itinerary to state."""

    expected = DraftItinerary(
        title="Architecture Day",
        summary="A compact architecture-focused Chicago day.",
        stops=[],
    )

    mock_generate_itinerary.return_value = expected

    state = {
        "user_message": "Plan an architecture day.",
        "trip_request": {
            "date": "2026-08-08",
            "start_time": "11:00",
            "end_time": "20:00",
            "start_location": "Hyde Park",
            "end_location": "Union Station",
            "group_type": "family",
            "group_size": 3,
            "interests": ["architecture"],
            "dietary_preferences": [],
            "budget": 150.0,
            "pace": None,
            "walking_tolerance": "limited",
            "preferred_neighborhoods": [],
            "excluded_neighborhoods": [],
            "must_include": [],
            "must_avoid": [],
            "indoor_outdoor_preference": None,
        },
        "retrieved_places": [],
    }

    result = planner_node(state)

    assert "draft_itinerary" in result
    actual = DraftItinerary.model_validate(
        result["draft_itinerary"]
    )

    assert actual == expected

    mock_generate_itinerary.assert_called_once()

    context = mock_generate_itinerary.call_args.args[0]

    assert context.trip_request.interests == ["architecture"]
    assert context.candidate_places == []