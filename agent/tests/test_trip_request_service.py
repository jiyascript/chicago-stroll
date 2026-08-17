import datetime
from app.schemas import TripRequest, TripRequestUpdate
from app.services.trip_request import merge_trip_request

def test_merge_trip_request_preserves_existing_values() -> None:
    """A partial update should not erase previously known details."""

    current = TripRequest(
        start_time="11:00",
        end_time="20:00",
        start_location="Hyde Park",
        end_location="Union Station",
        interests=["architecture"],
        dietary_preferences=["vegetarian"],
        budget=150,
        walking_tolerance="limited",
    )

    update = TripRequestUpdate(
        date=datetime.date(2026, 8, 8),
    )

    merged = merge_trip_request(current, update)

    assert merged.date == datetime.date(2026, 8, 8)
    assert merged.start_location == "Hyde Park"
    assert merged.end_location == "Union Station"
    assert merged.budget == 150
    assert merged.interests == ["architecture"]