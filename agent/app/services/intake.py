"""utilities for evaluating completeness"""
from app.schemas import TripRequest

REQUIRED_PLANNING_FIELDS = (
    "date", 
    "start_time",
    "end_time",
    "start_location",
)

def find_missing_fields(request: TripRequest) -> list[str]:
    """Return a list of missing required fields in the trip request."""
    missing_fields = []
    for field in REQUIRED_PLANNING_FIELDS:
        if getattr(request, field) is None:
            missing_fields.append(field)
    return missing_fields