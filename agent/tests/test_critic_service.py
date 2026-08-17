from app.schemas import (
    DraftItinerary,
    ItineraryStop,
    Place,
    RetrievedPlace,
    TripRequest,
)
from app.services.critic_service import (
    critique_itinerary,
)


def make_place(
    name: str,
    category: str = "museum",
    tags: list[str] | None = None,
    typical_visit_minutes: int = 60,
) -> Place:
    """Create deterministic test place data."""

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
        typical_visit_minutes=typical_visit_minutes,
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


def retrieved(
    place: Place,
    candidate_id: str,
) -> RetrievedPlace:
    """Wrap a place as a retrieved candidate."""

    return RetrievedPlace(
        candidate_id=candidate_id,
        place=place,
        score=10.0,
        matched_tags=[],
        retrieval_reasons=[
            "Test candidate"
        ],
    )


def test_critic_flags_missing_food_stop() -> None:
    request = TripRequest(
        start_time="11:00",
        end_time="13:00",
        start_location="Hyde Park",
        dietary_preferences=[
            "vegetarian"
        ],
    )

    museum = make_place(
        "Museum A"
    )

    restaurant = make_place(
        "Vegetarian Restaurant",
        category="restaurant",
        tags=["vegetarian"],
    )

    museum_candidate = retrieved(
        museum,
        "C1",
    )

    restaurant_candidate = retrieved(
        restaurant,
        "C2",
    )

    itinerary = DraftItinerary(
        title="Test Day",
        summary="Test itinerary.",
        stops=[
            ItineraryStop(
                candidate_id="C1",
                arrival_time="11:00",
                departure_time="12:00",
                reason="Test.",
            ),
        ],
    )

    result = critique_itinerary(
        request=request,
        itinerary=itinerary,
        candidates=[
            museum_candidate,
            restaurant_candidate,
        ],
    )

    assert result.is_valid is False

    assert any(
        "dietary" in issue.lower()
        or "food" in issue.lower()
        for issue in result.issues
    )


def test_critic_uses_canonical_visit_duration() -> None:
    request = TripRequest(
        start_time="11:00",
        end_time="16:00",
        start_location="Loop",
    )

    museum = make_place(
        "Museum A",
        typical_visit_minutes=60,
    )

    museum_candidate = retrieved(
        museum,
        "C1",
    )

    itinerary = DraftItinerary(
        title="Bad Duration",
        summary="Test.",
        stops=[
            ItineraryStop(
                candidate_id="C1",
                arrival_time="11:00",
                departure_time="16:00",
                reason="Test.",
            ),
        ],
    )

    result = critique_itinerary(
        request=request,
        itinerary=itinerary,
        candidates=[
            museum_candidate
        ],
    )

    assert result.is_valid is False

    assert any(
        "typical visit duration" in issue
        for issue in result.issues
    )


def test_critic_rejects_unknown_candidate_id() -> None:
    request = TripRequest(
        start_time="11:00",
        end_time="12:00",
        start_location="Loop",
    )

    museum = make_place(
        "Museum A"
    )

    museum_candidate = retrieved(
        museum,
        "C1",
    )

    itinerary = DraftItinerary(
        title="Invented Place",
        summary="Test.",
        stops=[
            ItineraryStop(
                candidate_id="C999",
                arrival_time="11:00",
                departure_time="12:00",
                reason="Test.",
            ),
        ],
    )

    result = critique_itinerary(
        request=request,
        itinerary=itinerary,
        candidates=[
            museum_candidate
        ],
    )

    assert result.is_valid is False

    assert any(
        "candidate_id" in issue.lower()
        for issue in result.issues
    )


def test_critic_flags_insufficient_travel_time() -> None:
    request = TripRequest(
        start_time="11:00",
        end_time="14:00",
        start_location="Loop",
    )

    place_a = make_place(
        "Place A",
    )

    place_b = make_place(
        "Place B",
    )

    place_a.latitude = 41.8781
    place_a.longitude = -87.6298

    place_b.latitude = 41.9000
    place_b.longitude = -87.6298

    candidate_a = retrieved(
        place_a,
        "C1",
    )

    candidate_b = retrieved(
        place_b,
        "C2",
    )

    itinerary = DraftItinerary(
        title="Impossible Travel",
        summary="Test.",
        stops=[
            ItineraryStop(
                candidate_id="C1",
                arrival_time="11:00",
                departure_time="12:00",
                reason="Test.",
            ),
            ItineraryStop(
                candidate_id="C2",
                arrival_time="12:05",
                departure_time="13:00",
                reason="Test.",
            ),
        ],
    )

    result = critique_itinerary(
        request=request,
        itinerary=itinerary,
        candidates=[
            candidate_a,
            candidate_b,
        ],
    )

    assert result.is_valid is False

    assert any(
        "travel time" in issue.lower()
        for issue in result.issues
    )