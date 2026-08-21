"""LangGraph node that generates a clarification question."""

from langchain_core.messages import HumanMessage, SystemMessage

from app.config import create_model
from app.schemas import TripRequest
from app.state import PlannerState
from app.services.model_invocation import invoke_runnable_with_fallback
from app.config.model import create_model,get_fallback_model_name
SYSTEM_PROMPT = """
You are the clarification assistant for Chicago Stroll.

You receive:
1. The information already extracted about the trip.
2. The required fields that are still missing.

Write one friendly follow-up question that asks for all missing information
naturally.

Do not repeat information that is already known.
Do not recommend places or start planning yet.
"""


def create_clarification(state: PlannerState) -> dict:
    """Generate a clarification question."""

    trip_request_data = state.get("trip_request")

    if trip_request_data is None:
        raise ValueError(
            "trip_request must exist before creating clarification."
        )

    trip_request = TripRequest.model_validate(
        trip_request_data
    )

    primary_model = create_model()
    fallback_model = create_model(get_fallback_model_name())

    prompt = f"""
Current trip request:

{trip_request.model_dump_json(indent=2)}

Missing fields:

{state.get("missing_fields", [])}
"""
    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT,
        ),
        HumanMessage(
            content=prompt,
        ),
    ]

    response = invoke_runnable_with_fallback(
        primary=primary_model,
        fallback=fallback_model,
        payload=messages,
    )
    content = response.content

    if isinstance(content, str):
        clarification_question = content
    elif isinstance(content, list):
        clarification_question = "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
            and block.get("type") == "text"
        )
    else:
        clarification_question = str(content)

    return {
        "clarification_question": clarification_question,
        "ready_for_research": False,
    }