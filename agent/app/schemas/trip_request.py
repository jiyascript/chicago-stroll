from pydantic import BaseModel, Field

class TripRequest(BaseModel):
    date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    start_location: str | None = None
    end_location: str | None = None
    group_type: str | None = None
    group_size: int | None = None
    interests: list[str] = Field(default_factory=list)
    dietary_preferences: list[str] = Field(default_factory=list)
    budget: float | None = None
    pace: str | None = None
    walking_tolerance: str | None = None
    preferred_neighborhoods: list[str] = Field(default_factory=list)
    excluded_neighborhoods: list[str] = Field(default_factory=list)
    must_include: list[str] = Field(default_factory=list)
    must_avoid: list[str] = Field(default_factory=list)
    indoor_outdoor_preference: str | None = None

class TripRequestUpdate(BaseModel):
    date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    start_location: str | None = None
    end_location: str | None = None
    group_type: str | None = None
    group_size: int | None = None
    interests: list[str] | None = None
    dietary_preferences: list[str] | None = None
    budget: float | None = None
    pace: str | None = None
    walking_tolerance: str | None = None
    preferred_neighborhoods: list[str] | None = None
    excluded_neighborhoods: list[str] | None = None
    must_include: list[str] | None = None
    must_avoid: list[str] | None = None
    indoor_outdoor_preference: str | None = None
