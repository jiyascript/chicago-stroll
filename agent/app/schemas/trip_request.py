from typing import Literal
import datetime 
from pydantic import BaseModel, Field, ConfigDict
class TripRequest(BaseModel):
    """Structured representation of a user's trip preferences."""

    model_config = ConfigDict(
        extra="forbid")
    
    date: datetime.date | None = Field(
        default=None,
        description="The date of the outing, when explicitly stated or inferable.",
    )

    start_time: str | None = Field(
        default=None, description="The start time of the trip in 24-hour HH:MM format.",
    )

    end_time: str | None = Field(
        default=None, description="The end time of the trip in 24-hour HH:MM format.",
    )

    start_location: str | None = Field(
        default=None, description="The neighborhood,landmark, address, hotel, airport, or station where the user wants the plan to begin"
    )

    end_location: str | None = Field(
        default = None, description = "The location where the user must finish, when different from teh starting location"
    )

    group_type: Literal[
        "solo",
        "couple",
        "friends",
        "family",
        "business",
        "other",
    ] | None = Field(
        default=None,
        description="The general type of group taking the outing.",
    )

    group_size: int | None = Field(
        default = None, 
        ge = 1,
        description = "Total number of people when starting",
    )
    
    interests: list[str] | None = Field(
        default=None, description="Activities or topics or subjects or experiences the user is interested in",
    )

    dietary_preferences: list[str] = Field(
        default_factory=list,
        description="Food preferences, allergies, and dietary restrictions.",
    )

    budget: float | None = Field(
        default=None,
        ge=0,
        description="The user's total budget in US dollars.",
    )

    pace: Literal["relaxed", "balanced", "packed"] | None = Field(
        default=None,
        description="The desired pace of the itinerary.",
    )

    walking_tolerance: Literal[ "minimal", "limited", "moderate", "high",] | None = Field(
        default=None, description="How much walking the user/group is comfortable doing",
    )
    
    preferred_neighborhoods: list[str] = Field(
        default_factory=list,
        description="Neighborhoods the user prefers to visit.",
    )
    
    excluded_neighborhoods: list[str] = Field(
        default_factory=list,
        description="Neighborhoods the user wants to avoid.",
    )

    must_include: list[str] = Field(
        default_factory=list,
        description="Specific places or experiences that must be included.",
    )

    must_avoid: list[str] = Field(
        default_factory=list,
        description="Experiences, environments, or place types the user wants to avoid.",
    )   

    indoor_outdoor_preference: Literal[
        "indoor",
        "outdoor",
        "mixed",
    ] | None = Field(
        default=None,
        description="Whether the user prefers indoor, outdoor, or mixed plans.",
    )


