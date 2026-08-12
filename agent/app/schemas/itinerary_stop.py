"""Schema representing one stop in an itinerary."""

from pydantic import BaseModel
from app.schemas.places import Place


class ItineraryStop(BaseModel):
    """One stop in a generated itinerary."""
    place: Place
    arrival_time: str
    departure_time: str
    reason: str