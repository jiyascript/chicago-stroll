from pydantic import BaseModel
from app.schemas.places import Place

class RetrievedPlace(BaseModel):
    candidate_id: str | None = None
    place: Place
    score: float
    matched_tags: list[str]
    retrieval_reasons: list[str]