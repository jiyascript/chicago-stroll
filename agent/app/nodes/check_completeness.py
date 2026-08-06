"""LangGraph node that checks whether the trip request is complete"""

from app.services.intake import find_missing_fields
from app.state import PlannerState

def check_completeness(state: PlannerState)-> dict:

    trip_request = state["trip_request"]
    if trip_request is None:
        raise ValueError("trip_request must be created before checking completeness.")
    
    missing_fields = find_missing_fields(trip_request)
    return {
        "missing_fields": missing_fields,
    }