"""Prompt construction for the Chicago Stroll itinerary planner."""

from app.schemas import PlannerContext


def format_list(values: list[str]) -> str:
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

        matched_tags = format_list(candidate.matched_tags)

        candidate_sections.append(
            f"""
Candidate {index}

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

    trip_section = "\n".join(trip_lines)

    candidates_section = (
        "\n\n".join(candidate_sections)
        if candidate_sections
        else "No candidate places were retrieved."
    )

    return f"""
You are the itinerary planning component for Chicago Stroll.

Your job is to create a realistic, enjoyable Chicago itinerary using the
structured trip request and the retrieved candidate places below.

You MUST use only places included in the candidate list.
Do not invent additional restaurants, attractions, neighborhoods, or venues.

TRIP REQUEST
------------

{trip_section}


CANDIDATE PLACES
----------------

{candidates_section}


PLANNING REQUIREMENTS
---------------------

Create the best itinerary possible for this user.

Follow these rules:

1. Respect the requested start time and end time.

2. Use only the candidate places provided above.

3. Prefer places with stronger retrieval scores when they also fit the
   overall itinerary.

4. Prioritize places matching the user's interests, group type, walking
   tolerance, neighborhood preferences, and indoor/outdoor preference.

5. Respect excluded neighborhoods and anything listed under must_avoid.

6. Include anything under must_include whenever a matching candidate exists.

7. Use each selected place at most once.

8. Use each place's typical_visit_minutes when estimating how long a stop
   should last.

9. Keep the itinerary geographically sensible. Avoid unnecessary travel
   between distant neighborhoods.

10. Account for the user's start location and end location when choosing the
    overall sequence.

11. Do not create an overly packed itinerary. Leave reasonable transition
    time between stops.

12. If walking tolerance is limited or minimal, strongly favor compact routes
    and places requiring minimal walking.

13. Consider public transit accessibility when ordering places.

14. Prefer an enjoyable variety of activities rather than scheduling many
    highly similar stops consecutively.

15. Respect known opening hours when they are provided. If hours are unknown,
    do not invent them.

16. Treat the result as a draft itinerary. Do not claim that uncertain
    operational details such as current hours, reservations, or transit
    conditions have been verified unless that information was provided.

17. Give each stop a concise reason explaining why it fits this specific
    user's trip.

18. Arrival and departure times must use 24-hour HH:MM format.

Return a DraftItinerary matching the required structured output schema.
""".strip()