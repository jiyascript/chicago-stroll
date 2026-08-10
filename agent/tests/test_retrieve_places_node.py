"""Tests for the retrieve places LangGraph node."""

from unittest.mock import patch

from app.nodes.retrieve_places import retrieve_places_node
from app.schemas import Place, RetrievedPlace


def make_retrieved_place() -> RetrievedPlace:
    """Create a deterministic retrieved place for testing."""

    place = Place(
        provider_id="test-place-1",
        name="Test Architecture Museum",
        category="museum",
        ambiance=["historic", "local"],
        neighborhood="Loop",
        description="A test museum.",
        tags=["architecture", "history"],
        price_tier="free",
        typical_visit_minutes=60,
        best_time_of_day="afternoon",
        indoor_outdoor="indoor",
        weather_suitability=["any"],
        walking_required="minimal",
        transit_access="excellent",
        group_friendly=["solo", "friends", "family"],
        opening_hours={},
        reservation_required=False,
        website=None,
        local_score=9,
        why_visit="Useful for testing retrieval.",
        address=None,
        longitude=-87.63,
        latitude=41.88,
        source_categories=[],
        source_opening_hours=None,
    )

    return RetrievedPlace(
        place=place,
        score=12.0,
        matched_tags=["architecture"],
        retrieval_reasons=[
            "Matches architecture interest",
            "Excellent public transit",
        ],
    )


@patch("app.nodes.retrieve_places.retrieve_places")
@patch("app.nodes.retrieve_places.PlaceRepository")
def test_retrieve_places_node_updates_state(
    mock_repository_class,
    mock_retrieve_places,
) -> None:
    """The node should add retrieved candidates to graph state."""

    expected_candidate = make_retrieved_place()

    mock_repository = mock_repository_class.return_value

    mock_retrieve_places.return_value = [
        expected_candidate
    ]

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
        "missing_fields": [],
        "clarification_question": None,
        "ready_for_research": True,
    }

    result = retrieve_places_node(state)

    assert "retrieved_places" in result
    assert len(result["retrieved_places"]) == 1

    candidate = result["retrieved_places"][0]

    assert candidate.place.name == "Test Architecture Museum"
    assert candidate.score == 12.0
    assert candidate.matched_tags == ["architecture"]

    mock_retrieve_places.assert_called_once()

    call_kwargs = mock_retrieve_places.call_args.kwargs

    assert call_kwargs["repository"] is mock_repository
    assert call_kwargs["request"].interests == ["architecture"]