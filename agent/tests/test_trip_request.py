from app.schemas import TripRequest
def test_trip_request_accepts_valid_data() -> None:
    request = TripRequest(
        start_time="10:00",
        end_time="19:00",
        interests=["bookstores", "art"],
        dietary_preferences=["vegetarian"],
        budget=70.0,
        pace="relaxed",
    )
    assert request.start_time == "10:00"
    assert request.end_time == "19:00"
    assert "art" in request.interests
    assert request.budget == 70.0