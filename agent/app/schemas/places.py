from pydantic import BaseModel, Field

class RawPlace(BaseModel):
    provider_id: str
    name: str
    address: str | None = None
    neighborhood: str | None = None
    provider_categories: list[str] = Field(default_factory=list)
    longitude: float
    latitude: float
    website: str | None = None
    opening_hours: str | None = None
    is_free: bool | None = None

class Place(BaseModel):
    provider_id: str
    name: str
    category: str = "attraction"
    ambiance: list[str] = Field(default_factory=list)
    neighborhood: str = "Chicago"
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    price_tier: str = "unknown"
    typical_visit_minutes: int = 60
    best_time_of_day: str = "any"
    indoor_outdoor: str = "mixed"
    weather_suitability: list[str] = Field(default_factory=lambda:["any"])
    walking_required: str = "moderate"
    transit_access: str = "good"
    group_friendly: list[str] = Field(default_factory=list)
    opening_hours: dict | str | None = None
    reservation_required: bool = False
    website: str | None = None
    local_score: float = 5.0
    why_visit: str = ""
    address: str | None = None
    longitude: float
    latitude: float
    source_categories: list[str] = Field(default_factory=list)
    source_opening_hours: str | None = None

class RetrievedPlace(BaseModel):
    candidate_id: str | None = None
    place: Place
    score: float = 0.0
    matched_tags: list[str] = Field(default_factory=list)
    retrieval_reasons: list[str] = Field(default_factory=list)
