"""LangGraph node that parses the user's request"""

from langchain_core.messages import HumanMessage, SystemMessage
from app.config import create_model
from app.prompts.intake import INTAKE_SYSTEM_PROMPT
from app.schemas import TripRequest
from app.state import PlannerState

def parse_request(state: PlannerState) -> dict:

    model = create_model()
    structured_model = model.with_structured_output(TripRequest)
    trip_request = structured_model.invoke(
        [
            SystemMessage(content=INTAKE_SYSTEM_PROMPT,),
            HumanMessage(content=state["user_message"]),
        ]
    )
    return {
        "trip_request": trip_request.model_dump(),
    }