from app.schemas import (
    DraftItinerary,
    ItineraryStop,
    Place,
    TripRequest,
)
from app.services.critic_service import critique_itinerary


def make_place(
    name: str,
    category: str = "museum",
) -> Place:
    return Place(
        provider_id=name,
        name=name,
        category=category,
        ambiance=["local"],
        neighborhood="Loop",
        description="Test place.",
        tags=[],
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


def test_critic_flags_missing_food_stop() -> None:
    request = TripRequest(
        start_time="11:00",
        end_time="20:00",
        start_location="Hyde Park",
        dietary_preferences=["vegetarian"],
    )

    itinerary = DraftItinerary(
        title="Test Day",
        summary="Test itinerary.",
        stops=[
            ItineraryStop(
                place=make_place("Museum A"),
                arrival_time="11:00",
                departure_time="12:00",
                reason="Test.",
            ),
        ],
    )

    result = critique_itinerary(
        request=request,
        itinerary=itinerary,
    )

    assert result.is_valid is False

    assert any(
        "food stop" in issue
        for issue in result.issues
    )