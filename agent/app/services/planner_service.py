from app.config.model import create_model, get_fallback_model_name
from app.prompts.planner_prompt import build_planner_prompt
from app.schemas import DraftItinerary,PlannerContext
from app.services.model_invocation import invoke_runnable_with_fallback

def generate_itinerary(context: PlannerContext,) -> DraftItinerary:

    prompt = build_planner_prompt(context)
    primary_model=create_model()
    fallback_model = create_model(get_fallback_model_name())
    primary=primary_model.with_structured_output(DraftItinerary)
    fallback=fallback_model.with_structured_output(DraftItinerary)
    itinerary = invoke_runnable_with_fallback(
        primary=primary,
        fallback=fallback,
        payload=prompt
    )
    return itinerary