"""Tests for the itinerary repair node."""

from unittest.mock import patch

from app.nodes.repair import repair_node
from app.schemas import (
    DraftItinerary,
    Place,
    RetrievedPlace,
)


def make_candidate() -> RetrievedPlace:
    """Create a retrieved candidate for repair testing."""

    place = Place(
        provider_id="museum-a",
        name="Museum A",
        category="museum",
        ambiance=["local"],
        neighborhood="Loop",
        description="Test museum.",
        tags=["architecture"],
        price_tier="free",
        typical_visit_minutes=60,
        best_time_of_day="any",
        indoor_outdoor="indoor",
        weather_suitability=["any"],
        walking_required="minimal",
        transit_access="excellent",
        group_friendly=["family"],
        opening_hours={},
        reservation_required=False,
        website=None,
        local_score=8,
        why_visit="Test.",
        address=None,
        longitude=-87.63,
        latitude=41.88,
        source_categories=[],
        source_opening_hours=None,
    )

    return RetrievedPlace(
        place=place,
        score=10.0,
        matched_tags=[
            "architecture"
        ],
        retrieval_reasons=[
            "Test candidate"
        ],
    )


@patch(
    "app.nodes.repair.repair_itinerary"
)
def test_repair_node_updates_itinerary_and_count(
    mock_repair_itinerary,
) -> None:
    """Repair should update itinerary and increment repair count."""

    repaired = DraftItinerary(
        title="Repaired Chicago Day",
        summary="A corrected itinerary.",
        stops=[],
    )

    mock_repair_itinerary.return_value = (
        repaired
    )

    candidate = make_candidate()

    state = {
        "trip_request": {
            "date": "2026-08-08",
            "start_time": "11:00",
            "end_time": "20:00",
            "start_location": "Hyde Park",
            "end_location": "Union Station",
            "group_type": "family",
            "group_size": 3,
            "interests": [
                "architecture"
            ],
            "dietary_preferences": [
                "vegetarian"
            ],
            "budget": 150.0,
            "pace": None,
            "walking_tolerance": (
                "limited"
            ),
            "preferred_neighborhoods": [],
            "excluded_neighborhoods": [],
            "must_include": [],
            "must_avoid": [],
            "indoor_outdoor_preference": None,
        },
        "retrieved_places": [
            candidate.model_dump(
                mode="json"
            )
        ],
        "draft_itinerary": {
            "title": "Bad Draft",
            "summary": "Needs repair.",
            "stops": [],
        },
        "critique_result": {
            "is_valid": False,
            "issues": [
                (
                    "The itinerary "
                    "contains no stops."
                )
            ],
            "warnings": [],
        },
        "repair_count": 0,
    }

    result = repair_node(
        state
    )

    assert (
        result["repair_count"]
        == 1
    )

    actual = (
        DraftItinerary.model_validate(
            result[
                "draft_itinerary"
            ]
        )
    )

    assert actual == repaired

    mock_repair_itinerary.assert_called_once()

    repair_context = (
        mock_repair_itinerary
        .call_args
        .args[0]
    )

    assert (
        len(
            repair_context
            .candidate_places
        )
        == 1
    )

    assert (
        repair_context
        .candidate_places[0]
        .place
        .provider_id
        == "museum-a"
    )