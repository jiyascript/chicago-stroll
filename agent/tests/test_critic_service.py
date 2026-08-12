from app.schemas import (
    DraftItinerary,
    ItineraryStop,
    Place,
    TripRequest,
    RetrievedPlace
)
from app.services.critic_service import critique_itinerary


def make_place(
    name: str,
    category: str = "museum",
    tags: list[str] | None = None,
) -> Place:
    return Place(
        provider_id=name.lower().replace(
            " ",
            "-",
        ),
        name=name,
        category=category,
        ambiance=["local"],
        neighborhood="Loop",
        description="Test place.",
        tags=tags or [],
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

    museum = make_place(
        "Museum A"
    )

    vegetarian_restaurant = make_place(
        "Vegetarian Restaurant",
        category="restaurant",
        tags=["vegetarian"],
    )

    itinerary = DraftItinerary(
        title="Test Day",
        summary="Test itinerary.",
        stops=[
            ItineraryStop(
                provider_id=museum.provider_id,
                arrival_time="11:00",
                departure_time="12:00",
                reason="Test.",
            ),
        ],
    )

    candidates = [
        RetrievedPlace(
            place=museum,
            score=10.0,
            matched_tags=[],
            retrieval_reasons=[
                "Test candidate"
            ],
        ),
        RetrievedPlace(
            place=vegetarian_restaurant,
            score=9.0,
            matched_tags=[
                "vegetarian"
            ],
            retrieval_reasons=[
                "Matches dietary preferences"
            ],
        ),
    ]

    result = critique_itinerary(
        request=request,
        itinerary=itinerary,
        candidates=candidates,
    )

    assert result.is_valid is False

    assert any(
        "dietary" in issue.lower()
        or "food" in issue.lower()
        for issue in result.issues
    )