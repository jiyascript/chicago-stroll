"""Prompt construction for itinerary repair."""

from app.schemas import RepairContext


def build_repair_prompt(
    context: RepairContext,
) -> str:
    """Build the prompt used to repair an invalid itinerary."""

    request = context.trip_request
    itinerary = context.draft_itinerary
    critique = context.critique_result

    issues = "\n".join(
        f"- {issue}"
        for issue in critique.issues
    )

    warnings = (
        "\n".join(
            f"- {warning}"
            for warning in critique.warnings
        )
        if critique.warnings
        else "- None"
    )

    return f"""
You are the itinerary repair component for Chicago Stroll.

Your job is to correct an existing draft itinerary based on structured
validation feedback.

Do NOT redesign the entire itinerary unless necessary.

Preserve good parts of the existing itinerary and make the smallest reasonable
changes needed to resolve the reported issues.

TRIP REQUEST
------------

{request.model_dump_json(indent=2)}


CURRENT DRAFT ITINERARY
-----------------------

{itinerary.model_dump_json(indent=2)}


VALIDATION ISSUES
-----------------

{issues}


WARNINGS
--------

{warnings}


REPAIR REQUIREMENTS
-------------------

1. Fix every validation issue listed above.

2. Preserve stops that are already compatible with the user's request unless
   changing them is necessary to resolve an issue.

3. Do not invent new factual information such as opening hours, addresses,
   prices, or transit conditions.

4. Do not schedule a stop outside known opening hours.

5. Respect the user's requested start and end times.

6. Respect walking tolerance, neighborhood exclusions, dietary preferences,
   and other explicit constraints.

7. Avoid duplicate places.

8. Keep stop timing realistic and chronological.

9. Preserve geographic coherence where possible.

10. If a food stop is required, prefer an existing food candidate already
    present in the draft when possible. Do not invent a new venue.

11. Return a complete repaired DraftItinerary, not a patch or explanation.

Return only data matching the DraftItinerary structured output schema.
""".strip()