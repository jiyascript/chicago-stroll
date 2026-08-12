from app.repositories import PlaceRepository
from app.schemas import TripRequest
from app.services.place_retrieval import retrieve_places
from app.state import PlannerState

def retrieve_places_node(state: PlannerState,) -> dict:
    """Retrieve candidate places for the trip."""

    trip_request = TripRequest.model_validate(
        state["trip_request"]
    )

    repository = PlaceRepository()

    candidates = retrieve_places(
        repository=repository,
        request=trip_request,
    )

    return {
        "retrieved_places": [
            candidate.model_dump(mode="json")
            for candidate in candidates
        ],
    }