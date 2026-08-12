"""Routing functions for the Chicago Stroll graph"""

from typing import Literal
from app.state import PlannerState


def route_initial_request(
    state: PlannerState,
) -> Literal["parse_request", "update_request"]:
    """Choose whether to parse a new request or update an existing one."""

    if state.get("trip_request") is None:
        return "parse_request"

    return "update_request"
def route_after_completeness(state: PlannerState) -> Literal["create_clarification", "ready_for_research"]:
    """Choose the next node after checking completeness"""
    if state["missing_fields"]:
        return "create_clarification"
    return "ready_for_research"

MAX_REPAIRS = 2
def route_after_critic(state: PlannerState):
    critique = state["critique_result"]

    if critique["is_valid"]:
        return "finished"

    return "repair"
