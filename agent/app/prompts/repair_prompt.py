"""Prompt construction for itinerary repair."""

from app.schemas import RepairContext


def build_repair_prompt(
    context: RepairContext,
) -> str:
    """Build the prompt used to repair an invalid itinerary."""

    request = context.trip_request
    itinerary = context.draft_itinerary
    critique = context.critique_result

    issues = (
        "\n".join(
            f"- {issue}"
            for issue in critique.issues
        )
        if critique.issues
        else "- None"
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

Your job is to repair an existing draft itinerary based on deterministic
validation feedback.

Do NOT redesign the entire itinerary unless necessary.

Make the smallest reasonable set of changes needed to resolve the reported
issues while preserving valid parts of the existing itinerary.

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


OUTPUT CONTRACT
---------------

Each itinerary stop must contain ONLY:

- provider_id
- arrival_time
- departure_time
- reason

Do NOT return full Place objects.

Do NOT invent provider IDs.

Do NOT modify or recreate authoritative place metadata.

You may change only:

- which existing provider_id is selected
- stop order
- arrival_time
- departure_time
- reason

You may NOT create or modify:

- place names
- categories
- tags
- descriptions
- coordinates
- opening hours
- typical visit durations
- prices
- neighborhoods
- transit access
- dietary metadata

Candidate metadata is owned by the application and must remain authoritative.


REPAIR REQUIREMENTS
-------------------

1. Fix every validation issue listed above.

2. Preserve stops that already satisfy the user's request unless changing them
   is necessary to fix an issue.

3. Make minimal changes rather than regenerating the itinerary from scratch.

4. Never invent factual information.

5. Never invent a venue or provider_id.

6. Respect the user's requested start and end times.

7. Respect walking tolerance, neighborhood exclusions, dietary preferences,
   and other explicit constraints.

8. Avoid duplicate provider IDs.

9. Keep stop timing realistic and chronological.

10. Do not extend a stop far beyond its normal visit duration merely to fill
    the requested time window.

11. If the itinerary cannot reasonably fill the entire requested window using
    valid candidates, leave reasonable unused time rather than manipulating
    candidate metadata or stop duration.

12. Preserve geographic coherence where possible.

13. If a dietary-compatible food stop is needed, use only an existing
    retrieved provider_id whose metadata supports that dietary preference.

14. Do not claim a generic food venue satisfies a dietary preference unless
    its authoritative tags support that claim.

15. Return a complete repaired DraftItinerary, not a patch, explanation, or
    commentary.

Return only data matching the DraftItinerary structured output schema.
""".strip()