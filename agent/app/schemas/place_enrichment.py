"""LLM-generated planning metadata for a place."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class PlaceEnrichment(BaseModel):
    """Planner-specific attributes inferred for a Chicago place."""

    model_config = ConfigDict(extra="forbid")
    category: Literal[
        "restaurant",
        "cafe",
        "bar",
        "museum",
        "gallery",
        "park",
        "landmark",
        "bookstore",
        "shop",
        "neighborhood_experience",
        "music_venue",
        "theater",
        "other",
    ]

    description: str

    ambiance: list[
        Literal[
            "cozy",
            "quiet",
            "lively",
            "romantic",
            "historic",
            "trendy",
            "luxury",
            "family-friendly",
            "creative",
            "local",
            "touristy",
        ]
    ] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)

    price_tier: Literal[
        "free",
        "$",
        "$$",
        "$$$",
        "$$$$",
    ]

    typical_visit_minutes: int = Field(ge=15)

    best_time_of_day: Literal[
        "morning",
        "afternoon",
        "evening",
        "night",
        "any",
    ]

    indoor_outdoor: Literal[
        "indoor",
        "outdoor",
        "mixed",
    ]

    weather_suitability: list[
        Literal[
            "any",
            "sunny",
            "rain",
            "cold",
            "snow",
        ]
    ]

    walking_required: Literal[
        "minimal",
        "moderate",
        "high",
    ]

    transit_access: Literal[
        "poor",
        "fair",
        "good",
        "excellent",
    ]

    group_friendly: list[
        Literal[
            "solo",
            "couple",
            "friends",
            "family",
            "kids",
            "business",
        ]
    ]

    local_score: int = Field(
        ge=1,
        le=10,
    )

    why_visit: str

    reservation_required: bool = False