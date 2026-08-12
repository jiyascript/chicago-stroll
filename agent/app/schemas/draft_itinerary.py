"""Schema representing a generated itinerary."""
from pydantic import BaseModel
from app.schemas.itinerary_stop import ItineraryStop

class DraftItinerary(BaseModel):
    """Planner output."""
    title: str
    summary: str
    stops: list[ItineraryStop]