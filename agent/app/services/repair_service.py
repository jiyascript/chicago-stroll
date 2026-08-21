"""LLM service for repairing invalid itineraries."""

from app.config.model import create_model, get_fallback_model_name
from app.prompts.repair_prompt import build_repair_prompt
from app.schemas import DraftItinerary, RepairContext
from app.services.model_invocation import invoke_runnable_with_fallback

def repair_itinerary(context: RepairContext,) -> DraftItinerary:
    """Repair an itinerary using structured critic feedback."""

    prompt = build_repair_prompt(context)
    primary_model = create_model()
    fallback_model=create_model(get_fallback_model_name())
    primary=primary_model.with_structured_output(DraftItinerary)
    fallback=fallback_model.with_structured_output(DraftItinerary)
    repaired = invoke_runnable_with_fallback(primary=primary,fallback=fallback,payload=prompt)
    return repaired