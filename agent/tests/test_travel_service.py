from app.schemas import Place
from app.services.travel_service import (
    distance_km,
    estimate_travel_minutes,
)


def make_place(
    name: str,
    latitude: float,
    longitude: float,
) -> Place:
    """Create a deterministic Place for travel tests."""

    return Place(
        provider_id=name.lower().replace(" ", "-"),
        name=name,
        category="landmark",
        ambiance=["historic"],
        neighborhood="Loop",
        description="Test place.",
        tags=["architecture"],
        price_tier="free",
        typical_visit_minutes=30,
        best_time_of_day="afternoon",
        indoor_outdoor="outdoor",
        weather_suitability=["any"],
        walking_required="minimal",
        transit_access="excellent",
        group_friendly=["family"],
        opening_hours={},
        reservation_required=False,
        website=None,
        local_score=8,
        why_visit="Test place.",
        address=None,
        longitude=longitude,
        latitude=latitude,
        source_categories=[],
        source_opening_hours=None,
    )


def test_distance_between_different_places_is_positive() -> None:
    place_a = make_place(
        name="Place A",
        latitude=41.8781,
        longitude=-87.6298,
    )

    place_b = make_place(
        name="Place B",
        latitude=41.8840,
        longitude=-87.6240,
    )

    assert distance_km(
        place_a,
        place_b,
    ) > 0


def test_same_place_uses_minimum_travel_time() -> None:
    place = make_place(
        name="Place A",
        latitude=41.8781,
        longitude=-87.6298,
    )

    assert estimate_travel_minutes(
        place,
        place,
    ) == 10


def test_nearby_places_use_short_travel_time() -> None:
    place_a = make_place(
        name="Place A",
        latitude=41.8781,
        longitude=-87.6298,
    )

    place_b = make_place(
        name="Place B",
        latitude=41.8860,
        longitude=-87.6298,
    )

    assert estimate_travel_minutes(
        place_a,
        place_b,
    ) == 20