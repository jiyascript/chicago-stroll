"""Tests for the itinerary repair node."""

from unittest.mock import patch

from app.nodes.repair import repair_node
from app.schemas import DraftItinerary


@patch("app.nodes.repair.repair_itinerary")
def test_repair_node_updates_itinerary_and_count(
    mock_repair_itinerary,
) -> None:
    """The repair node should replace the draft and increment repair count."""

    repaired = DraftItinerary(
        title="Repaired Chicago Day",
        summary="A corrected itinerary.",
        stops=[],
    )

    mock_repair_itinerary.return_value = repaired

    state = {
        "trip_request": {
            "date": "2026-08-08",
            "start_time": "11:00",
            "end_time": "20:00",
            "start_location": "Hyde Park",
            "end_location": "Union Station",
            "group_type": "family",
            "group_size": 3,
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
        },
        "draft_itinerary": {
            "title": "Bad Draft",
            "summary": "Needs repair.",
            "stops": [],
        },
        "critique_result": {
            "is_valid": False,
            "issues": [
                "The itinerary contains no stops."
            ],
            "warnings": [],
        },
        "repair_count": 0,
    }

    result = repair_node(state)

    assert result["repair_count"] == 1

    actual = DraftItinerary.model_validate(
        result["draft_itinerary"]
    )

    assert actual == repaired

    mock_repair_itinerary.assert_called_once()