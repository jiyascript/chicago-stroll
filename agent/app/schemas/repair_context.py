"""Context to provide to the repair agent"""
from pydantic import BaseModel
from app.schemas.critique_result import CritiqueResult
from app.schemas.draft_itinerary import DraftItinerary
from app.schemas.trip_request import TripRequest

class RepairContext(BaseModel):
    trip_request: TripRequest
    draft_itinerary: DraftItinerary
    critique_result: CritiqueResult