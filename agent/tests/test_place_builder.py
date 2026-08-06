"""Tests for building final Place records."""

from app.schemas import PlaceEnrichment, RawPlace
from app.services.place_builder import build_place


def test_build_place_prefers_api_free_status() -> None:
    """API-backed free admission should override LLM price estimates."""

    raw_place = RawPlace(
        provider_id="example-id",
        name="Example Museum",
        address="123 Example Street, Chicago, IL",
        neighborhood="Loop",
        provider_categories=[
            "entertainment.museum",
            "no_fee",
        ],
        longitude=-87.63,
        latitude=41.88,
        website="https://example.com",
        opening_hours="Mo-Fr 10:00-16:00",
        is_free=True,
    )

    enrichment = PlaceEnrichment(
        category="museum",
        description="A small Chicago museum.",
        ambiance=["historic", "quiet"],
        tags=["history", "architecture"],
        price_tier="$",
        typical_visit_minutes=45,
        best_time_of_day="afternoon",
        indoor_outdoor="indoor",
        weather_suitability=[
            "any",
            "rain",
            "cold",
        ],
        walking_required="minimal",
        transit_access="excellent",
        group_friendly=[
            "solo",
            "couple",
            "family",
        ],
        local_score=8,
        why_visit="Explore a distinctive part of Chicago history.",
        reservation_required=False,
    )

    place = build_place(
        raw_place=raw_place,
        enrichment=enrichment,
    )

    assert place.price_tier == "free"
    assert place.weather_suitability == ["any"]
    assert place.name == "Example Museum"
    assert place.neighborhood == "Loop"
    assert place.source_opening_hours == "Mo-Fr 10:00-16:00"