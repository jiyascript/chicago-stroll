"""Shared state for the Chicago Stroll planning workflow"""

from typing import TypedDict, NotRequired
from app.schemas import TripRequest
from app.schemas import RetrievedPlace

class PlannerState(TypedDict):
    """Information shared between every LangGraph node."""

    user_message: str
    trip_request: NotRequired[TripRequest | None]
    missing_fields: NotRequired[list[str]]
    clarification_question: NotRequired[str | None]
    ready_for_research: NotRequired[bool]
    retrieved_places: list[RetrievedPlace]