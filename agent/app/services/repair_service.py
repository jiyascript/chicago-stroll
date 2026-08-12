"""LLM service for repairing invalid itineraries."""

from app.config import create_model
from app.prompts.repair_prompt import build_repair_prompt
from app.schemas import DraftItinerary, RepairContext


def repair_itinerary(context: RepairContext,) -> DraftItinerary:
    """Repair an itinerary using structured critic feedback."""

    prompt = build_repair_prompt(context)
    model = create_model()

    repair_model = model.with_structured_output(DraftItinerary)
    repaired = repair_model.invoke(prompt)

    return repaired