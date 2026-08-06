"""Normalized factual place data from external APIs."""

from pydantic import BaseModel, ConfigDict, Field


class RawPlace(BaseModel):
    """Basic factual place information before LLM enrichment."""

    model_config = ConfigDict(extra="forbid")

    provider_id: str

    name: str

    address: str | None = None

    neighborhood: str | None = None

    provider_categories: list[str] = Field(
        default_factory=list,
    )

    longitude: float
    latitude: float
    website: str | None = None
    opening_hours: str | None = None
    is_free: bool | None = None