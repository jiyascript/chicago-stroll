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


def evaluate_place(
    place: Place,
    request: TripRequest,
) -> RetrievedPlace:
    """Score a place and record why it matches the trip."""

    score = 0.0
    reasons: list[str] = []

    requested_interests = {
        interest.lower()
        for interest in request.interests
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
        for neighborhood in request.preferred_neighborhoods
    }

    if place.neighborhood.lower() in preferred:
        score += 3
        reasons.append(
            "Located in a preferred neighborhood"
        )

    excluded = {
        neighborhood.lower()
        for neighborhood in request.excluded_neighborhoods
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
    """Retrieve the best candidate places for a trip."""

    return rank_places(
        places=repository.all(),
        request=request,
        top_k=top_k,
    )