"""Context provided to the itinerary planner."""

from pydantic import BaseModel
from app.schemas import RetrievedPlace, TripRequest

class PlannerContext(BaseModel):
    """Everything the planner needs."""

    trip_request: TripRequest
    candidate_places: list[RetrievedPlace]