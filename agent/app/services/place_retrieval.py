"""Deterministic scoring and explainable retrieval for Chicago places."""

from app.repositories import PlaceRepository
from app.schemas import (
    Place,
    RetrievedPlace,
    TripRequest,
)


WALKING_ORDER = {
    "minimal": 0,
    "moderate": 1,
    "high": 2,
}
FOOD_CATEGORIES = {
    "restaurant",
    "cafe",
}


def normalize_values(
    values: list[str],
) -> set[str]:
    """Normalize text values for retrieval comparisons."""

    return {
        value.strip().lower()
        for value in values
    }

def evaluate_place(
    place: Place,
    request: TripRequest,
) -> RetrievedPlace:
    """Score a place and record why it matches the trip."""

    score = 0.0
    reasons: list[str] = []

    requested_interests = {
        interest.lower()
        for interest in (request.interests or [])
    }

    place_tags = {
        tag.lower()
        for tag in place.tags
    }

    matched_tags = sorted(
        requested_interests & place_tags
    )

    if matched_tags:
        score += 5 * len(matched_tags)

        reasons.append(
            "Matches requested interests: "
            + ", ".join(matched_tags)
        )

    preferred = {
        neighborhood.lower()
        for neighborhood in (request.preferred_neighborhoods or [])
    }

    if place.neighborhood.lower() in preferred:
        score += 3
        reasons.append(
            "Located in a preferred neighborhood"
        )

    excluded = {
        neighborhood.lower()
        for neighborhood in (request.excluded_neighborhoods or [])
    }

    if place.neighborhood.lower() in excluded:
        score -= 100
        reasons.append(
            "Located in an excluded neighborhood"
        )

    if (
        request.group_type
        and request.group_type in place.group_friendly
    ):
        score += 2
        reasons.append(
            f"Suitable for {request.group_type} groups"
        )

    if request.indoor_outdoor_preference:
        if (
            place.indoor_outdoor
            == request.indoor_outdoor_preference
        ):
            score += 2
            reasons.append(
                "Matches indoor/outdoor preference"
            )
        elif place.indoor_outdoor == "mixed":
            score += 1
            reasons.append(
                "Offers mixed indoor/outdoor activity"
            )

    if request.walking_tolerance:
        tolerance_map = {
            "minimal": 0,
            "limited": 0,
            "moderate": 1,
            "high": 2,
        }

        allowed = tolerance_map[
            request.walking_tolerance
        ]

        required = WALKING_ORDER[
            place.walking_required
        ]

        if required <= allowed:
            score += 2
            reasons.append(
                "Compatible with walking tolerance"
            )
        else:
            score -= 4
            reasons.append(
                "Requires more walking than preferred"
            )

    if place.transit_access == "excellent":
        score += 2
        reasons.append(
            "Excellent public transit access"
        )

    elif place.transit_access == "good":
        score += 1
        reasons.append(
            "Good public transit access"
        )

    local_bonus = place.local_score / 5
    score += local_bonus

    if place.local_score >= 8:
        reasons.append(
            "Strong Chicago-specific experience"
        )
        # Dietary compatibility.
    dietary_preferences = normalize_values(
        request.dietary_preferences or []
    )

    place_tags = normalize_values(
        place.tags
    )

    dietary_matches = (
        dietary_preferences
        & place_tags
    )
    matched_tags = sorted(
        set(matched_tags)
        | dietary_matches
    )

    if (
        place.category in FOOD_CATEGORIES
        and dietary_matches
    ):
        score += 6 * len(dietary_matches)

        reasons.append(
            "Matches dietary preferences: "
            + ", ".join(
                sorted(dietary_matches)
            )
        )
        # Food venue quality.
    if place.category in FOOD_CATEGORIES:
        if place.local_score >= 8:
            score += 1

            reasons.append(
                "Strong local food option"
            )

        if (
            request.group_type
            and request.group_type
            in place.group_friendly
        ):
            score += 1

            reasons.append(
                "Food venue suits the group"
            )

    return RetrievedPlace(
        place=place,
        score=score,
        matched_tags=matched_tags,
        retrieval_reasons=reasons,
    )


def rank_places(
    places: list[Place],
    request: TripRequest,
    top_k: int = 15,
) -> list[RetrievedPlace]:
    """Rank places by compatibility with the trip."""

    ranked = [
        evaluate_place(
            place=place,
            request=request,
        )
        for place in places
    ]

    ranked.sort(
        key=lambda candidate: candidate.score,
        reverse=True,
    )

    return ranked[:top_k]

def retrieve_places(
    repository: PlaceRepository,
    request: TripRequest,
    top_k: int = 15,
) -> list[RetrievedPlace]:
    """Retrieve a diverse set of relevant trip candidates."""

    all_places = repository.all()

    ranked = rank_places(
        places=all_places,
        request=request,
        top_k=len(all_places),
    )

    # No special food requirement.
    if not request.dietary_preferences:
        return ranked[:top_k]

    dietary = normalize_values(
        request.dietary_preferences
    )

    compatible_food = [
        candidate
        for candidate in ranked
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

    other_food = [
        candidate
        for candidate in ranked
        if (
            candidate.place.category
            in FOOD_CATEGORIES
            and candidate
            not in compatible_food
        )
    ]

    food_candidates = (
        compatible_food
        + other_food
    )

    non_food_candidates = [
        candidate
        for candidate in ranked
        if candidate.place.category
        not in FOOD_CATEGORIES
    ]

    # Reserve part of retrieval context for food.
    food_limit = min(
        5,
        len(food_candidates),
    )

    attraction_limit = max(
        0,
        top_k - food_limit,
    )

    selected = (
        non_food_candidates[
            :attraction_limit
        ]
        + food_candidates[
            :food_limit
        ]
    )

    selected.sort(
        key=lambda candidate: candidate.score,
        reverse=True,
    )

    return selected