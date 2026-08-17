from pydantic import BaseModel

from app.schemas.places import Place

class ResolvedItineraryStop(BaseModel):
    place: Place
    arrival_time: str
    departure_time: str
    reason: str
class ResolvedItinerary(BaseModel):
    title:str
    summary:str
    stops:list[ResolvedItineraryStop]