"""Tests for the TripRequest schema."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas import TripRequest


def test_trip_request_accepts_valid_data() -> None:
    """A valid request should create a TripRequest object."""

    request = TripRequest(
        date=date(2026, 8, 8),
        start_time="11:00",
        end_time="20:00",
        start_location="Hyde Park",
        end_location="Union Station",
        group_type="family",
        interests=["architecture"],
        dietary_preferences=["vegetarian"],
        budget=150,
        pace="relaxed",
        walking_tolerance="limited",
    )

    assert request.start_location == "Hyde Park"
    assert request.end_location == "Union Station"
    assert request.group_type == "family"
    assert request.walking_tolerance == "limited"
    assert request.budget == 150


def test_trip_request_rejects_unknown_fields() -> None:
    """Typo fields should be rejected instead of silently ignored."""

    with pytest.raises(ValidationError):
        TripRequest(
            start_trip="11:00",
        )