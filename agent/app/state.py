"""Shared state for the Chicago Stroll planning workflow"""
from langgraph.graph.message import add_messages
from typing import TypedDict, NotRequired, Annotated

class PlannerState(TypedDict):
    """Information shared between every LangGraph node."""

    user_message: str
    trip_request: NotRequired[dict | None]
    missing_fields: NotRequired[list[str]]
    clarification_question: NotRequired[str | None]
    ready_for_research: NotRequired[bool]
    retrieved_places: NotRequired[list[dict]]
    draft_itinerary: NotRequired[dict]
    critique_result: NotRequired[dict]
    repair_count: NotRequired[int]
    messages: Annotated[list, add_messages]
    planner_steps: NotRequired[int]
    