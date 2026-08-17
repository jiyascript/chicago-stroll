from app.schemas import (
    DraftItinerary,
    ItineraryStop,
    Place,
    RetrievedPlace,
)
from app.services.itinerary_hydration import (
    hydrate_itinerary,
)


def make_candidate() -> RetrievedPlace:
    place = Place(
        provider_id="museum-1",
        name="Architecture Museum",
        category="museum",
        ambiance=["historic"],
        neighborhood="Loop",
        description="A test architecture museum.",
        tags=["architecture"],
        price_tier="free",
        typical_visit_minutes=60,
        best_time_of_day="afternoon",
        indoor_outdoor="indoor",
        weather_suitability=["any"],
        walking_required="minimal",
        transit_access="excellent",
        group_friendly=["family"],
        opening_hours={},
        reservation_required=False,
        website=None,
        local_score=8,
        why_visit="Good architecture.",
        address=None,
        longitude=-87.63,
        latitude=41.88,
        source_categories=[],
        source_opening_hours=None,
    )

    return RetrievedPlace(
        candidate_id="museum-1",
        place=place,
        score=10,
        matched_tags=["architecture"],
        retrieval_reasons=["Matches architecture"],
    )


def test_hydrate_itinerary_resolves_place() -> None:
    candidate = make_candidate()

    itinerary = DraftItinerary(
        title="Architecture Day",
        summary="Test itinerary.",
        stops=[
            ItineraryStop(
                candidate_id="museum-1",
                arrival_time="11:00",
                departure_time="12:00",
                reason="Architecture.",
            )
        ],
    )

    result = hydrate_itinerary(
        itinerary=itinerary,
        candidates=[candidate],
    )

    assert len(result.stops) == 1
    assert (
        result.stops[0].place.name
        == "Architecture Museum"
    )
    assert (
        result.stops[0].place.typical_visit_minutes
        == 60
    )


def test_hydrate_itinerary_rejects_unknown_id() -> None:
    candidate = make_candidate()

    itinerary = DraftItinerary(
        title="Bad itinerary",
        summary="Test.",
        stops=[
            ItineraryStop(
                candidate_id="fake-id",
                arrival_time="11:00",
                departure_time="12:00",
                reason="Test.",
            )
        ],
    )

    try:
        hydrate_itinerary(
            itinerary=itinerary,
            candidates=[candidate],
        )
    except ValueError as exc:
        assert "unknown provider_id" in str(exc)
    else:
        raise AssertionError(
            "Expected hydration to reject unknown provider_id."
        )