from app.schemas import DraftItinerary, RetrievedPlace, TripRequest
from app.services.critic_service import critique_itinerary
from app.state import PlannerState


def critic_node(state: PlannerState) -> dict:
    req = TripRequest.model_validate(state["trip_request"])
    draft = DraftItinerary.model_validate(state["draft_itinerary"])

    candidates = [
        RetrievedPlace.model_validate(x)
        for x in state.get("retrieved_places", [])
    ]

    result = critique_itinerary(req, draft, candidates)

    update = {
        "critique_result": result.model_dump(mode="json"),
    }

    if result.is_valid:
        update["final_status"] = "finished"

    return update