from app.repositories import PlaceRepository
from app.schemas import TripRequest
from app.services.planner_tools import SearchPlaces, GetTravelTime, run_search, run_travel

def _req():
    return TripRequest.model_validate({
        "date": "2026-08-08", "start_time": "11:00", "end_time": "20:00",
        "start_location": "Hyde Park", "interests": ["architecture"],
    })

def test_run_search_assigns_stable_ids_and_dedups():
    repo, req, registry = PlaceRepository(), _req(), []
    _, registry = run_search(repo, req, SearchPlaces(limit=5), registry)
    ids = [c["candidate_id"] for c in registry]
    assert ids == [f"C{i+1}" for i in range(len(registry))]      # stable, ordered
    before = len(registry)
    _, registry = run_search(repo, req, SearchPlaces(limit=5), registry)
    assert len(registry) == before                               # no duplicates
    assert len({c["place"]["provider_id"] for c in registry}) == before
def test_run_travel_rejects_unknown_id():
    assert "Unknown" in run_travel([], GetTravelTime(
        from_candidate_id="C1", to_candidate_id="C2"))