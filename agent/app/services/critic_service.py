"""Deterministic validation for draft itineraries."""

from datetime import datetime

from app.schemas import (
    CritiqueResult,
    DraftItinerary,
    RetrievedPlace,
    TripRequest,
)
from app.services.travel_service import (
    estimate_travel_minutes,
)


TIME_FORMAT = "%H:%M"

FOOD_CATEGORIES = {
    "restaurant",
    "cafe",
}


def normalize_values(
    values: list[str] | None,
) -> set[str]:
    """Normalize strings for deterministic comparisons."""

    return {
        value.strip().lower()
        for value in (values or [])
    }


def parse_time(
    value: str,
) -> datetime:
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
    """Validate an itinerary against canonical retrieved candidates."""

    issues: list[str] = []
    warnings: list[str] = []

    if not itinerary.stops:
        return CritiqueResult(
            is_valid=False,
            issues=[
                "Itinerary contains no stops."
            ],
            warnings=[],
        )

    # candidate_id -> canonical Place
    candidate_lookup = {
        candidate.candidate_id: candidate.place
        for candidate in candidates
        if candidate.candidate_id is not None
    }

    # 1. Candidate IDs must come from retrieval.
    for stop in itinerary.stops:
        if stop.candidate_id not in candidate_lookup:
            issues.append(
                (
                    "The itinerary references an unknown "
                    f"candidate_id: {stop.candidate_id}."
                )
            )

    # Only use resolvable stops for checks that need Place data.
    valid_stops = [
        stop
        for stop in itinerary.stops
        if stop.candidate_id in candidate_lookup
    ]

    # 2. Duplicate places.
    candidate_ids = [
        stop.candidate_id
        for stop in itinerary.stops
    ]

    if len(candidate_ids) != len(
        set(candidate_ids)
    ):
        issues.append(
            "The itinerary contains duplicate places."
        )

    # 3. Requested start time.
    if request.start_time:
        requested_start = parse_time(
            request.start_time
        )

        actual_start = parse_time(
            itinerary.stops[0].arrival_time
        )

        if actual_start < requested_start:
            issues.append(
                (
                    "The itinerary starts before "
                    "the requested start time."
                )
            )

    # 4. Requested end time.
    if request.end_time:
        requested_end = parse_time(
            request.end_time
        )

        actual_end = parse_time(
            itinerary.stops[-1].departure_time
        )

        if actual_end > requested_end:
            issues.append(
                (
                    "The itinerary ends after "
                    "the requested end time."
                )
            )

        unused_minutes = int(
            (
                requested_end
                - actual_end
            ).total_seconds()
            / 60
        )

        if unused_minutes >= 180:
            warnings.append(
                (
                    "The itinerary leaves a large amount "
                    "of unused time before the latest end time."
                )
            )

    # 5. Chronological ordering.
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
            previous_place = candidate_lookup.get(
                previous.candidate_id
            )

            current_place = candidate_lookup.get(
                current.candidate_id
            )

            previous_name = (
                previous_place.name
                if previous_place
                else previous.candidate_id
            )

            current_name = (
                current_place.name
                if current_place
                else current.candidate_id
            )

            issues.append(
                (
                    f"{current_name} begins before "
                    f"{previous_name} ends."
                )
            )

    # 6. Travel feasibility.
    for current, next_stop in zip(
        itinerary.stops,
        itinerary.stops[1:],
    ):
        current_place = candidate_lookup.get(
            current.candidate_id
        )

        next_place = candidate_lookup.get(
            next_stop.candidate_id
        )

        if (
            current_place is None
            or next_place is None
        ):
            continue

        departure = parse_time(
            current.departure_time
        )

        next_arrival = parse_time(
            next_stop.arrival_time
        )

        available_minutes = int(
            (
                next_arrival
                - departure
            ).total_seconds()
            / 60
        )

        required_minutes = (
            estimate_travel_minutes(
                current_place,
                next_place,
            )
        )

        if available_minutes < required_minutes:
            issues.append(
                (
                    "Insufficient travel time between "
                    f"{current_place.name} and "
                    f"{next_place.name}: "
                    f"{available_minutes} minutes available, "
                    f"approximately {required_minutes} required."
                )
            )

    # 7. Walking tolerance.
    if request.walking_tolerance in {
        "minimal",
        "limited",
    }:
        high_walking: list[str] = []

        for stop in valid_stops:
            place = candidate_lookup[
                stop.candidate_id
            ]

            if place.walking_required == "high":
                high_walking.append(
                    place.name
                )

        if high_walking:
            issues.append(
                (
                    "The itinerary includes high-walking "
                    "stops despite limited walking tolerance: "
                    + ", ".join(high_walking)
                )
            )

    # 8. Excluded neighborhoods.
    excluded = normalize_values(
        request.excluded_neighborhoods
    )

    for stop in valid_stops:
        place = candidate_lookup[
            stop.candidate_id
        ]

        if (
            place.neighborhood.lower()
            in excluded
        ):
            issues.append(
                (
                    f"{place.name} is in excluded "
                    f"neighborhood {place.neighborhood}."
                )
            )

    # 9. Dietary compatibility.
    if request.dietary_preferences:
        dietary = normalize_values(
            request.dietary_preferences
        )

        compatible_food_candidates = [
            candidate
            for candidate in candidates
            if (
                candidate.place.category
                in FOOD_CATEGORIES
                and dietary.intersection(
                    normalize_values(
                        candidate.place.tags
                    )
                )
            )
        ]

        if compatible_food_candidates:
            compatible_food_stop = any(
                (
                    candidate_lookup[
                        stop.candidate_id
                    ].category
                    in FOOD_CATEGORIES
                )
                and dietary.intersection(
                    normalize_values(
                        candidate_lookup[
                            stop.candidate_id
                        ].tags
                    )
                )
                for stop in valid_stops
            )

            if not compatible_food_stop:
                issues.append(
                    (
                        "Compatible dietary food candidates "
                        "were retrieved, but the itinerary "
                        "does not include one."
                    )
                )

        else:
            warnings.append(
                (
                    "No retrieved food candidate has verified "
                    "metadata matching the user's dietary preferences."
                )
            )

    # 10. Canonical visit-duration validation.
    for stop in valid_stops:
        place = candidate_lookup[
            stop.candidate_id
        ]

        arrival = parse_time(
            stop.arrival_time
        )

        departure = parse_time(
            stop.departure_time
        )

        actual_minutes = int(
            (
                departure - arrival
            ).total_seconds()
            / 60
        )

        if actual_minutes <= 0:
            issues.append(
                (
                    f"{place.name} has an invalid "
                    "arrival/departure interval."
                )
            )
            continue

        expected_minutes = (
            place.typical_visit_minutes
        )

        max_reasonable_minutes = max(
            expected_minutes * 2,
            expected_minutes + 60,
        )

        min_reasonable_minutes = max(
            15,
            expected_minutes // 2,
        )

        if actual_minutes > max_reasonable_minutes:
            issues.append(
                (
                    f"{place.name} is scheduled for "
                    f"{actual_minutes} minutes, but its "
                    f"typical visit duration is "
                    f"{expected_minutes} minutes."
                )
            )

        elif actual_minutes < min_reasonable_minutes:
            warnings.append(
                (
                    f"{place.name} is scheduled for only "
                    f"{actual_minutes} minutes, compared "
                    f"with a typical visit duration of "
                    f"{expected_minutes} minutes."
                )
            )

    return CritiqueResult(
        is_valid=not issues,
        issues=issues,
        warnings=warnings,
    )