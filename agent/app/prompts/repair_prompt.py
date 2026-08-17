"""Prompt construction for itinerary repair."""

from app.schemas import RepairContext


def format_list(
    values: list[str] | None,
) -> str:
    """Format values for the repair prompt."""

    return (
        ", ".join(values)
        if values
        else "None"
    )


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

    candidate_sections: list[str] = []

    for index, candidate in enumerate(
        context.candidate_places,
        start=1,
    ):
        place = candidate.place

        candidate_sections.append(
            f"""
Candidate ID: {candidate.candidate_id}
Name: {place.name}
Category: {place.category}
Neighborhood: {place.neighborhood}
Tags: {format_list(place.tags)}
Typical visit duration: {place.typical_visit_minutes} minutes
Walking required: {place.walking_required}
Transit access: {place.transit_access}
Opening hours: {place.source_opening_hours or "Unknown"}
Retrieval score: {candidate.score}
Matched tags: {format_list(candidate.matched_tags)}
""".strip()
        )

    candidates_section = (
        "\n\n".join(
            candidate_sections
        )
        if candidate_sections
        else "No retrieved candidates available."
    )

    return f"""
You are the itinerary repair component for Chicago Stroll.

Your job is to repair an existing draft itinerary based on deterministic
validation feedback.

Do NOT redesign the entire itinerary unless necessary.

Make the smallest reasonable changes needed to resolve the reported issues
while preserving valid parts of the existing itinerary.

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


RETRIEVED CANDIDATE PLACES
--------------------------

{candidates_section}


OUTPUT CONTRACT
---------------

Each itinerary stop must contain ONLY:

- candidate_id
- arrival_time
- departure_time
- reason

Every candidate_id must exactly match one of the retrieved candidate provider
IDs listed above.

Do NOT return full Place objects.

Do NOT invent provider IDs.

Do NOT modify or recreate authoritative place metadata.

You may change only:

- which retrieved candidate_id is selected
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

5. Never invent a venue or candidate_id.

6. Use only provider IDs from RETRIEVED CANDIDATE PLACES.

7. Respect the user's requested start and end times.

8. Respect walking tolerance, neighborhood exclusions, dietary preferences,
   and other explicit constraints.

9. Avoid duplicate provider IDs.

10. Keep stop timing realistic and chronological.

11. Base stop durations on each candidate's typical visit duration.

12. Do not extend a stop far beyond its typical visit duration merely to fill
    the requested time window.

13. If the itinerary cannot reasonably fill the entire requested window using
    valid candidates, leave reasonable unused time rather than manipulating
    stop duration or metadata.

14. Preserve geographic coherence where possible.

15. If a dietary-compatible food stop is needed, use only a retrieved
    restaurant or cafe whose tags explicitly support that dietary preference.

16. Do not claim a generic food venue satisfies a dietary preference unless
    its authoritative tags support that claim.

17. Return a complete repaired DraftItinerary, not a patch or explanation.

18. When the critic reports insufficient travel time between two stops,
    preserve the places when reasonable and adjust timing or ordering so that
    the gap between them is large enough for travel.

19. Do not solve travel-time violations by changing provider metadata or
    inventing shorter travel times.

Return only data matching the DraftItinerary structured output schema.
""".strip()