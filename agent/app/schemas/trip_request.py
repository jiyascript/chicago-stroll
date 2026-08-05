"""data models"""
from pydantic import BaseModel, Field 
class TripRequest(BaseModel):
    start_time: str | None = Field(
        default=None, description="The start time of the trip in 24-hour HH:MM format.",
    )
    end_time: str | None = Field(
        default=None, description="The end time of the trip in 24-hour HH:MM format.",
    )
    interests: list[str] | None = Field(
        default=None, description="Activities or topics the user is interested in",
    )

    dietary_preferences: list[str] = Field(
        default_factory=list,
        description="Food preferences or dietary restrictions.",
    )

    budget: float | None = Field(
        default=None,
        ge=0,
        description="The user's total budget in US dollars.",
    )

    pace: str | None = Field(
        default=None,
        description="The desired pace, such as relaxed, balanced, or packed.",
    )

