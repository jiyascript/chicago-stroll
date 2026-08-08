"""LangGraph node for merging a clarification answer into a trip request"""
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import create_model
from app.prompts.intake import TRIP_UPDATE_SYSTEM_PROMPT
from app.schemas import TripRequestUpdate, TripRequest
from app.services.trip_request import merge_trip_request
from app.state import PlannerState

def update_request(state: PlannerState)->dict:
    current_request_data = state.get("trip_request")

    if current_request_data is None:
        raise ValueError("trip_request must exist before applying an update.")

    current_request = TripRequest.model_validate(current_request_data)
    model = create_model()
    update_model = model.with_structured_output(TripRequestUpdate)

    prompt = f"""
Existing trip request:

{current_request.model_dump_json(indent=2)}

Newest user message:

{state["user_message"]}
"""

    update = update_model.invoke(
        [
            SystemMessage(content=TRIP_UPDATE_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    merged_request = merge_trip_request(
        current=current_request,
        update=update,
    )

    return {
        "trip_request": merged_request.model_dump(),
        "clarification_question": None,
        "ready_for_research": False,
    }