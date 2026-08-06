"""LangGraph node that generates a clarification question"""
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import create_model
from app.state import PlannerState

SYSTEM_PROMPT = """
You are the clarification assistant for Chicago Stroll.
You receive:
1. The information already extracted about the trip. 
2. The required fields that are still missing. 
Write ONE friendly followup question that asks for all of the missing information naturally. 
Do not repeat information that has already been provided and known. Do NOT recommend places or start planning yet."""

def create_clarification(state: PlannerState) -> dict:
    """Generate a clarification question."""

    model = create_model()
    trip_request = state.get("trip_request")

    if trip_request is None:
        raise ValueError(
            "Trip request must exist before creating clarification."
        )

    prompt = f"""
Current trip request:

{trip_request.model_dump_json(indent=2)}

Missing fields:

{state.get("missing_fields", [])}
"""

    response = model.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    content = response.content

    if isinstance(content, str):
        clarification_question = content
    elif isinstance(content, list):
        clarification_question = "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    else:
        clarification_question = str(content)

    return {
        "clarification_question": clarification_question,
        "ready_for_research": False,
    }