"""LangGraph node that parses the user's request"""

from langchain_core.messages import HumanMessage, SystemMessage
from app.prompts.intake import INTAKE_SYSTEM_PROMPT
from app.schemas import TripRequest
from app.state import PlannerState
from app.config.model import create_model, get_fallback_model_name
from app.services.model_invocation import invoke_runnable_with_fallback


def parse_request(state: PlannerState) -> dict:
    primary_model = create_model()
    primary=primary_model.with_structured_output(TripRequest)
    fallback_model=create_model(get_fallback_model_name())
    fallback=fallback_model.with_structured_output(TripRequest)
    messages = [
        SystemMessage(
            content=INTAKE_SYSTEM_PROMPT,
        ),
        HumanMessage(
            content=state["user_message"],
        ),
    ]

    trip_request = (
        invoke_runnable_with_fallback(
            primary=primary,
            fallback=fallback,
            payload=messages,
        )
    )

    return {
        "trip_request": (
            trip_request.model_dump()
        ),
    }