"""Routing functions for the Chicago Stroll graph"""

from typing import Literal
from app.state import PlannerState

def route_after_completeness(state: PlannerState) -> Literal["create_clarification", "ready_for_research"]:
    """Choose the next node after checking completeness"""
    if state["missing_fields"]:
        return "create_clarification"
    return "ready_for_research"
