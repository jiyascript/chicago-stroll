"""LLM enrichment for normalized Chicago place records."""

from langchain_core.messages import HumanMessage, SystemMessage
from app.config import create_model
from app.schemas import PlaceEnrichment, RawPlace


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

Rules:
- Do not invent addresses, websites, coordinates, or opening hours.
- Use only allowed enum values.
- Keep descriptions concise.
- If uncertain, choose conservative values.
- local_score measures how distinctive or representative the place is of
  Chicago, from 1 to 10.
"""


def enrich_place(raw_place: RawPlace) -> PlaceEnrichment:
    """Generate planning metadata for one normalized place."""

    model = create_model()
    enrichment_model = model.with_structured_output(PlaceEnrichment)

    return enrichment_model.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=raw_place.model_dump_json(indent=2)
            ),
        ]
    )