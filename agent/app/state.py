"""Shared state for the Chicago Stroll planning workflow"""

from typing import TypedDict
from app.schemas import TripRequest

class PlannerState(TypedDict):
    """info shared between every LangGraph node"""
    user_message: str
    trip_request:TripRequest | None
    missing_fields: list[str]
    clarification_question: str | None