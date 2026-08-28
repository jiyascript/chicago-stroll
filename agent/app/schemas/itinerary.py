from pydantic import BaseModel, Field
from app.schemas.places import Place

class ItineraryStop(BaseModel):
    candidate_id: str
    arrival_time: str
    departure_time: str
    reason: str

class DraftItinerary(BaseModel):
    title: str
    summary: str
    stops: list[ItineraryStop] = Field(min_length=1)

class ResolvedItineraryStop(BaseModel):
    place: Place
    arrival_time: str
    departure_time: str
    reason: str

class ResolvedItinerary(BaseModel):
    title: str
    summary: str
    stops: list[ResolvedItineraryStop]
