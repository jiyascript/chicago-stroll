from typing import Annotated, NotRequired, TypedDict
from langgraph.graph.message import add_messages

class PlannerState(TypedDict):
    user_message: str
    trip_request: NotRequired[dict | None]
    missing_fields: NotRequired[list[str]]
    clarification_question: NotRequired[str | None]
    ready_for_research: NotRequired[bool]
    retrieved_places: NotRequired[list[dict]]
    draft_itinerary: NotRequired[dict | None]
    critique_result: NotRequired[dict | None]
    recovery_decision: NotRequired[dict | None]
    recovery_feedback: NotRequired[str | None]
    messages: Annotated[list, add_messages]
    planner_steps: NotRequired[int]
    tool_call_count: NotRequired[int]
    repair_count: NotRequired[int]
    replan_count: NotRequired[int]
    final_status: NotRequired[str]
