"""Prompt construction for the Chicago Stroll itinerary planner."""

from app.schemas import PlannerContext


def format_list(values: list[str] | None) -> str:
    """Format a list for the planner prompt."""

    return ", ".join(values) if values else "None"


def build_planner_prompt(
    context: PlannerContext,
) -> str:
    """Build the itinerary planner prompt."""

    request = context.trip_request

    trip_lines = [
        f"Date: {request.date}",
        f"Start time: {request.start_time}",
        f"End time: {request.end_time}",
        f"Start location: {request.start_location}",
        f"End location: {request.end_location}",
        f"Group type: {request.group_type}",
        f"Group size: {request.group_size}",
        f"Budget: {request.budget}",
        f"Pace: {request.pace}",
        f"Walking tolerance: {request.walking_tolerance}",
        (
            "Indoor/outdoor preference: "
            f"{request.indoor_outdoor_preference}"
        ),
        f"Interests: {format_list(request.interests)}",
        (
            "Dietary preferences: "
            f"{format_list(request.dietary_preferences)}"
        ),
        (
            "Preferred neighborhoods: "
            f"{format_list(request.preferred_neighborhoods)}"
        ),
        (
            "Excluded neighborhoods: "
            f"{format_list(request.excluded_neighborhoods)}"
        ),
        f"Must include: {format_list(request.must_include)}",
        f"Must avoid: {format_list(request.must_avoid)}",
    ]

    candidate_sections: list[str] = []

    for index, candidate in enumerate(
        context.candidate_places,
        start=1,
    ):
        place = candidate.place

        reasons = (
            "\n".join(
                f"- {reason}"
                for reason in candidate.retrieval_reasons
            )
            if candidate.retrieval_reasons
            else "- No retrieval reasons provided"
        )

        matched_tags = format_list(
            candidate.matched_tags
        )

        candidate_sections.append(
            f"""
Candidate ID: {candidate.candidate_id}
Name: {place.name}
Category: {place.category}
Neighborhood: {place.neighborhood}
Description: {place.description}

Retrieval score: {candidate.score}
Matched tags: {matched_tags}

Retrieval reasons:
{reasons}

Typical visit duration: {place.typical_visit_minutes} minutes
Best time of day: {place.best_time_of_day}
Price tier: {place.price_tier}
Indoor/outdoor: {place.indoor_outdoor}
Walking required: {place.walking_required}
Transit access: {place.transit_access}
Group friendly: {format_list(place.group_friendly)}
Ambiance: {format_list(place.ambiance)}
Weather suitability: {format_list(place.weather_suitability)}
Reservation required: {place.reservation_required}
Opening hours: {place.source_opening_hours or "Unknown"}
Why visit: {place.why_visit}
""".strip()
        )

    trip_section = "\n".join(
        trip_lines
    )

    candidates_section = (
        "\n\n".join(candidate_sections)
        if candidate_sections
        else "No candidate places were retrieved."
    )

    return f"""
You are the itinerary planning component for Chicago Stroll.

Your job is to create a realistic and enjoyable Chicago itinerary using only
the structured trip request and retrieved candidate places below.

You may choose and schedule candidate places, but candidate metadata is
authoritative and must never be rewritten.

TRIP REQUEST
------------

{trip_section}


CANDIDATE PLACES
----------------

{candidates_section}


OUTPUT CONTRACT
---------------

Each itinerary stop must contain ONLY:

- candidate_id
- arrival_time
- departure_time
- reason

The candidate_id must exactly match one of the provider IDs in the candidate
list above.

Do NOT return full place objects.

Do NOT reproduce, rewrite, infer, or modify candidate metadata such as:

- place name
- category
- tags
- description
- coordinates
- opening hours
- typical visit duration
- price tier
- neighborhood
- transit access
- dietary metadata

The application will resolve candidate_id back to the authoritative Place
record after generation.


PLANNING REQUIREMENTS
---------------------

Create the best itinerary possible for this user.

Follow these rules:

1. Respect the requested start time and end time.

2. Use only candidate places provided above.

3. Prefer places with stronger retrieval scores when they also fit the overall
   itinerary.

4. Prioritize places matching the user's interests, group type, walking
   tolerance, neighborhood preferences, and indoor/outdoor preference.

5. Respect excluded neighborhoods and anything listed under must_avoid.

6. Include anything under must_include whenever a matching candidate exists.

7. Use each candidate_id at most once.

8. Use each candidate's typical_visit_minutes as the primary estimate for stop
   duration.

9. Never artificially extend a stop far beyond its typical visit duration just
   to fill the requested trip window.

10. If useful candidate activities do not fill the entire requested window,
    leave reasonable free time rather than fabricating duration.

11. Keep the itinerary geographically sensible and avoid unnecessary travel
    between distant neighborhoods.

12. Account for the user's start location and end location when choosing the
    overall sequence.

13. Do not create an overly packed itinerary. Leave reasonable transition time
    between stops.

14. If walking tolerance is limited or minimal, strongly favor compact routes
    and places requiring minimal walking.

15. Consider public transit accessibility when ordering places.

16. Prefer an enjoyable variety of activities rather than scheduling many
    highly similar stops consecutively.

17. Respect known opening hours when provided. If hours are unknown, do not
    invent them.

18. Treat the result as a draft itinerary. Do not claim uncertain operational
    details such as current hours, reservations, or transit conditions have
    been verified unless that information was provided.

19. Give each stop a concise reason explaining why it fits this user's trip.

20. Arrival and departure times must use 24-hour HH:MM format.

21. Never invent a restaurant, cafe, attraction, landmark, or candidate_id.

22. If dietary preferences are specified and one or more candidate restaurants
    or cafes explicitly contain matching dietary tags, you should strongly
    prefer one of those candidates.

23. If no candidate restaurant or cafe explicitly matches the requested
    dietary preference, do not invent or assume compatibility.

24. A restaurant without matching dietary tags may still be included for other
    reasons, but its reason must not claim that it satisfies the user's
    dietary preference.

25. Never infer dietary compatibility from cuisine alone.
    For example, an Indian, Mediterranean, or Mexican restaurant is NOT
    necessarily vegetarian unless the candidate tags explicitly say so.

26. Leave realistic travel time between consecutive stops. Nearby Loop stops
    generally need at least 10–20 minutes of transition time, while farther
    locations may require substantially more.

27. Do not schedule the next stop immediately after the previous stop unless
    the places are effectively colocated.

Return a DraftItinerary matching the required structured output schema.
""".strip()