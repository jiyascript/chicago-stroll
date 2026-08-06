"""Place schema for Chicago Stroll."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Place(BaseModel):
    """Structured representation of a Chicago place or experience."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        description="The place name as it should be displayed to the user."
    )

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
    ]

    neighborhood: str = Field(
        description="The Chicago neighborhood or area where the place is located."
    )

    description: str = Field(
        description="A concise description of what the place offers."
    )

    tags: list[str] = Field(
        default_factory=list,
        description="Interests, activities, and qualities associated with the place.",
    )

    price_tier: Literal[
        "free",
        "$",
        "$$",
        "$$$",
        "$$$$",
    ]

    typical_visit_minutes: int = Field(
        ge=15,
        description="Typical amount of time a visitor spends at the place.",
    )

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
    ] = Field(
        default_factory=lambda: ["any"],
    )

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
    ] = Field(
        default_factory=list,
    )

    opening_hours: dict[str, str] = Field(
        default_factory=dict,
    )

    reservation_required: bool = False

    website: str | None = None
    local_score: int = Field(
        ge=1,
        le=10,
        description=(
            "How uniquely representative of Chicago this place is. "
            "Higher values indicate a more iconic or local experience."
        ),
    )
    why_visit: str = Field(
        description=(
            "One sentence explaining what makes this place worth visiting."
        )
    )