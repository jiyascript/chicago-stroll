from app.config import create_model
from app.prompts.planner_prompt import build_planner_prompt
from app.schemas import (DraftItinerary,PlannerContext,)


def generate_itinerary(context: PlannerContext,) -> DraftItinerary:

    prompt = build_planner_prompt(context)
    model=create_model()
    planner = model.with_structured_output(DraftItinerary)
    itinerary = planner.invoke(prompt)
    return itinerary