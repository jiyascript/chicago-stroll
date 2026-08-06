"""Tests for the Place schema."""

import pytest
from pydantic import ValidationError

from app.schemas import Place


def test_place_accepts_valid_data() -> None:
    """A valid Chicago place should create a Place object."""

    place = Place(
        name="Chicago Cultural Center",
        category="landmark",
        neighborhood="Loop",
        description=(
            "A historic cultural building known for its architecture, "
            "exhibitions, and free public programming."
        ),
        tags=[
            "architecture",
            "art",
            "historic",
            "free",
        ],
        price_tier="free",
        typical_visit_minutes=75,
        best_time_of_day="afternoon",
        indoor_outdoor="indoor",
        weather_suitability=[
            "any",
            "rain",
            "cold",
            "snow",
        ],
        walking_required="minimal",
        transit_access="excellent",
        group_friendly=[
            "solo",
            "couple",
            "friends",
            "family",
            "business",
        ],
        opening_hours={
            "monday": "10:00-17:00",
            "tuesday": "10:00-17:00",
            "wednesday": "10:00-17:00",
            "thursday": "10:00-17:00",
            "friday": "10:00-17:00",
            "saturday": "10:00-17:00",
            "sunday": "10:00-17:00",
        },
        reservation_required=False,
        website="https://www.chicago.gov/city/en/depts/dca/supp_info/chicago_culturalcenter.html",
    )

    assert place.name == "Chicago Cultural Center"
    assert place.neighborhood == "Loop"
    assert place.price_tier == "free"
    assert place.transit_access == "excellent"
    assert "architecture" in place.tags
    assert "family" in place.group_friendly
    assert place.reservation_required is False


def test_place_rejects_unknown_fields() -> None:
    """Unknown fields should be rejected rather than silently ignored."""

    with pytest.raises(ValidationError):
        Place(
            name="Example Place",
            category="museum",
            neighborhood="Loop",
            description="Example description.",
            price_tier="$",
            typical_visit_minutes=60,
            best_time_of_day="afternoon",
            indoor_outdoor="indoor",
            walking_required="minimal",
            transit_access="good",
            mystery_field="unexpected",
        )