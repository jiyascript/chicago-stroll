"""Deterministic validation for draft itineraries."""

from datetime import datetime

from app.schemas import (
    CritiqueResult,
    DraftItinerary,
    TripRequest,
    RetrievedPlace
)


TIME_FORMAT = "%H:%M"


def parse_time(value: str) -> datetime:
    """Parse an HH:MM time string."""

    return datetime.strptime(
        value,
        TIME_FORMAT,
    )

def critique_itinerary(
    request: TripRequest,
    itinerary: DraftItinerary,
    candidates: list[RetrievedPlace],
) -> CritiqueResult:
    issues: list[str] = []
    warnings: list[str] = []

    candidate_ids = {
        candidate.place.provider_id
        for candidate in candidates
    }

    for stop in itinerary.stops:
        if stop.place.provider_id not in candidate_ids:
            issues.append(
                f"{stop.place.name} was not provided by the retrieval system."
            )
def critique_itinerary(
    request: TripRequest,
    itinerary: DraftItinerary,
    candidates: list[RetrievedPlace],
) -> CritiqueResult:
    """Validate an itinerary against user constraints."""

    issues: list[str] = []
    warnings: list[str] = []

    if not itinerary.stops:
        issues.append(
            "Itinerary contains no stops."
        )

        return CritiqueResult(
            is_valid=False,
            issues=issues,
            warnings=warnings,
        )

    # 1. Duplicate places.
    names = [
        stop.place.name
        for stop in itinerary.stops
    ]

    if len(names) != len(set(names)):
        issues.append(
            "The itinerary contains duplicate places."
        )

    # 2. Trip start time.
    if request.start_time:
        requested_start = parse_time(
            request.start_time
        )

        actual_start = parse_time(
            itinerary.stops[0].arrival_time
        )

        if actual_start < requested_start:
            issues.append(
                "The itinerary starts before the requested start time."
            )

    # 3. Trip end time.
    if request.end_time:
        requested_end = parse_time(
            request.end_time
        )

        actual_end = parse_time(
            itinerary.stops[-1].departure_time
        )

        if actual_end > requested_end:
            issues.append(
                "The itinerary ends after the requested end time."
            )

        # Ending far too early is not always invalid,
        # but it is worth flagging.
        unused_minutes = int(
            (
                requested_end
                - actual_end
            ).total_seconds()
            / 60
        )

        if unused_minutes >= 90:
            issues.append(
                "The itinerary ends significantly before the requested end time."
            )

    # 4. Stop ordering / overlap.
    for previous, current in zip(
        itinerary.stops,
        itinerary.stops[1:],
    ):
        previous_departure = parse_time(
            previous.departure_time
        )

        current_arrival = parse_time(
            current.arrival_time
        )

        if current_arrival < previous_departure:
            issues.append(
                (
                    f"{current.place.name} begins before "
                    f"{previous.place.name} ends."
                )
            )

    # 5. Walking tolerance.
    if request.walking_tolerance in {
        "minimal",
        "limited",
    }:
        high_walking = [
            stop.place.name
            for stop in itinerary.stops
            if stop.place.walking_required == "high"
        ]

        if high_walking:
            issues.append(
                (
                    "The itinerary includes high-walking stops "
                    "despite limited walking tolerance: "
                    + ", ".join(high_walking)
                )
            )

    # 6. Excluded neighborhoods.
    excluded = {
        neighborhood.lower()
        for neighborhood in request.excluded_neighborhoods
    }

    for stop in itinerary.stops:
        if stop.place.neighborhood.lower() in excluded:
            issues.append(
                (
                    f"{stop.place.name} is in excluded neighborhood "
                    f"{stop.place.neighborhood}."
                )
            )

    # 7. Missing food stop for dietary needs.
    if request.dietary_preferences:
        dietary = {
            preference.lower()
            for preference in request.dietary_preferences
        }

        compatible_food_stop = any(
            stop.place.category in {
                "restaurant",
                "cafe",
            }
            and dietary.intersection(
                {
                    tag.lower()
                    for tag in stop.place.tags
                }
            )
            for stop in itinerary.stops
        )

        if not compatible_food_stop:
            issues.append(
                "The itinerary does not include a food stop matching the user's dietary preferences."
            )

    return CritiqueResult(
        is_valid=not issues,
        issues=issues,
        warnings=warnings,
    )