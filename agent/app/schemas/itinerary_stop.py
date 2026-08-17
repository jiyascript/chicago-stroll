"""Schema representing one scheduled itinerary stop."""
from pydantic import BaseModel

class ItineraryStop(BaseModel):
    """One scheduled stop in an itinerary."""
    candidate_id: str
    arrival_time: str
    departure_time: str
    reason: str