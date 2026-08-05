"""Tests for intake completeness checking."""

from app.schemas import TripRequest
from app.services.intake import find_missing_fields


def test_find_missing_required_fields() -> None:
    """The checker should identify required fields that are absent."""

    request = TripRequest(
        start_time="11:00",
        interests=["architecture"],
    )

    missing = find_missing_fields(request)

    assert "date" in missing
    assert "end_time" in missing
    assert "start_location" in missing
    assert "start_time" not in missing