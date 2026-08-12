"""Structured result of itinerary validation"""
from pydantic import BaseModel, Field

class CritiqueResult(BaseModel):

    is_valid: bool
    issues: list[str] = Field(default_factory=list,)
    warnings: list[str] = Field(default_factory=list,)