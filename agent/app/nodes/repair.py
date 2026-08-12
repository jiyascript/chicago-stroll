"""LangGraph node for repairing invalid itineraries."""

from app.schemas import (
    CritiqueResult,
    DraftItinerary,
    RepairContext,
    TripRequest,
)
from app.services.repair_service import repair_itinerary
from app.state import PlannerState


def repair_node(
    state: PlannerState,
) -> dict:
    """Repair the current itinerary using critic feedback."""

    request = TripRequest.model_validate(
        state["trip_request"]
    )

    itinerary = DraftItinerary.model_validate(
        state["draft_itinerary"]
    )

    critique = CritiqueResult.model_validate(
        state["critique_result"]
    )

    context = RepairContext(
        trip_request=request,
        draft_itinerary=itinerary,
        critique_result=critique,
    )

    repaired_itinerary = repair_itinerary(
        context
    )

    repair_count = state.get(
        "repair_count",
        0,
    ) + 1

    print(
        f"Repairing itinerary — attempt {repair_count}"
    )

    return {
        "draft_itinerary": repaired_itinerary.model_dump(
            mode="json"
        ),
        "repair_count": repair_count,
    }