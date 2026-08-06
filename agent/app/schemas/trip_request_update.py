"""Partial updates to an existing trip request"""
import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class TripRequestUpdate(BaseModel):
    model_config = ConfigDict(extra = "forbid")
    date: datetime.date | None = Field(
        default=None, description="A newly provided or corrected outing date",

    )

    start_time: str | None = Field(
        default=None,
        description="A newly provided or corrected start time in HH:MM format.",
    )

    end_time: str | None = Field(
        default=None,
        description="A newly provided or corrected end time in HH:MM format.",
    )

    start_location: str | None = None
    end_location: str | None = None

    group_type: Literal[
        "solo",
        "couple",
        "friends",
        "family",
        "business",
        "other",
    ] | None = None

    group_size: int | None = Field(default=None, ge=1)

    interests: list[str] | None = None
    dietary_preferences: list[str] | None = None

    budget: float | None = Field(default=None, ge=0)

    pace: Literal["relaxed", "balanced", "packed"] | None = None

    walking_tolerance: Literal[
        "minimal",
        "limited",
        "moderate",
        "high",
    ] | None = None

    preferred_neighborhoods: list[str] | None = None
    excluded_neighborhoods: list[str] | None = None
    must_include: list[str] | None = None
    must_avoid: list[str] | None = None

    indoor_outdoor_preference: Literal[
        "indoor",
        "outdoor",
        "mixed",
    ] | None = None