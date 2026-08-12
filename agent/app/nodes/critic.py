"""LangGraph node for validating a draft itinerary"""

from app.schemas import DraftItinerary, TripRequest, RetrievedPlace
from app.services.critic_service import critique_itinerary
from app.state import PlannerState

def critic_node(state:PlannerState,) -> dict:
    """validate the current draft itinerary"""
    request = TripRequest.model_validate(state["trip_request"])
    itinerary= DraftItinerary.model_validate(state["draft_itinerary"])
    retrieved_places = [
        RetrievedPlace.model_validate(candidate)
        for candidate in state.get("retrieved_places", [])
    ]

    critique = critique_itinerary(
        request=request,
        itinerary=itinerary,
        candidates=retrieved_places,
    )
    print(
        "Critic:",
        critique.is_valid,
        critique.issues,
    )

    return {
        "critique_result": critique.model_dump(mode="json")
    }