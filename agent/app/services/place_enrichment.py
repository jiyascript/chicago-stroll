"""LLM enrichment for normalized Chicago place records."""

from langchain_core.messages import HumanMessage, SystemMessage

from app.config.model import create_model, get_fallback_model_name
from app.schemas import PlaceEnrichment, RawPlace
from app.services.model_invocation import invoke_runnable_with_fallback

SYSTEM_PROMPT = """
You enrich normalized Chicago place records for Chicago Stroll.

Use only the factual information provided.

Produce planner-oriented metadata such as:
- category
- concise description
- tags
- ambiance
- price tier
- typical visit duration
- best time of day
- indoor or outdoor suitability
- weather suitability
- walking level
- transit accessibility
- suitable group types
- local score
- why the place is worth visiting
- whether a reservation is usually required

TAG RULES:
- Tags should be useful for itinerary retrieval and matching user preferences.
- Include relevant concepts such as architecture, history, art, coffee,
  pizza, nightlife, family-friendly activities, or similar meaningful traits.
- For restaurants and cafes, include dietary compatibility when it is
  explicitly supported by the provided information.
- Useful dietary tags may include:
  vegetarian
  vegan
  gluten-free
  halal
  kosher
- Do not infer or invent dietary compatibility when the provided information
  does not support it.
- Do not label a generic restaurant or cafe as vegetarian or vegan merely
  because it may offer some suitable menu items.

Rules:
- Do not invent addresses, websites, coordinates, or opening hours.
- Use only allowed enum values.
- Keep descriptions concise.
- If uncertain, choose conservative values.
- local_score measures how distinctive or representative the place is of
  Chicago, from 1 to 10.
"""


def enrich_place(raw_place: RawPlace,) -> PlaceEnrichment:
    """Generate planning metadata for one normalized place."""

    primary_model = create_model()
    fallback_model= create_model(get_fallback_model_name())
    primary = primary_model.with_structured_output(PlaceEnrichment)
    fallback=fallback_model.with_structured_output(PlaceEnrichment)
    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        ),
        HumanMessage(
            content=raw_place.model_dump_json(
                indent=2
            )
        ),
    ]

    return invoke_runnable_with_fallback(
        primary=primary,
        fallback=fallback,
        payload=messages,
    )