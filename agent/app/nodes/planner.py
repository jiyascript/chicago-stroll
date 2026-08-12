from app.schemas import TripRequest, PlannerContext, RetrievedPlace
from app.services.planner_service import generate_itinerary
from app.state import PlannerState


def planner_node(state: PlannerState,) -> dict:
    """Generate a draft itinerary."""

    trip_request = TripRequest.model_validate(
        state["trip_request"]
    )
    retrieved_places = [
        RetrievedPlace.model_validate(candidate)
        for candidate in state.get(
            "retrieved_places",
            [],
        )
    ]
    context = PlannerContext(trip_request=trip_request,candidate_places=retrieved_places,)

    itinerary = generate_itinerary(context)

    return {
        "draft_itinerary": itinerary.model_dump(mode="json")
    }