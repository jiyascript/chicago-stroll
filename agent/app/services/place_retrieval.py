"""Deterministic scoring for Chicago place retrieval."""
from app.schemas import Place, TripRequest
from app.repositories import PlaceRepository

PRICE_ORDER = {
    "free": 0,
    "$": 1,
    "$$": 2,
    "$$$": 3,
    "$$$$": 4,
}
WALKING_ORDER = {
    "minimal": 0,
    "moderate": 1,
    "high": 2,
}


def score_place(place: Place,request: TripRequest,) -> float:
    """Score how well a place matches a trip request."""
    score = 0.0

    requested_interests = {
        interest.lower()
        for interest in request.interests
    }

    place_tags = {
        tag.lower()
        for tag in place.tags
    }

    # Strong signal: interests.
    interest_matches = requested_interests & place_tags
    score += 5 * len(interest_matches)

    # Preferred neighborhood.
    preferred = {
        neighborhood.lower()
        for neighborhood in request.preferred_neighborhoods
    }

    if place.neighborhood.lower() in preferred:
        score += 3

    # Explicit exclusions are hard penalties.
    excluded = {
        neighborhood.lower()
        for neighborhood in request.excluded_neighborhoods
    }

    if place.neighborhood.lower() in excluded:
        score -= 100

    # Group suitability.
    if (
        request.group_type
        and request.group_type in place.group_friendly
    ):
        score += 2

    # Indoor/outdoor preference.
    if request.indoor_outdoor_preference:
        if (
            place.indoor_outdoor
            == request.indoor_outdoor_preference
        ):
            score += 2
        elif place.indoor_outdoor == "mixed":
            score += 1

    # Walking compatibility.
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
        else:
            score -= 4

    # Transit-friendly bonus.
    if place.transit_access == "excellent":
        score += 2
    elif place.transit_access == "good":
        score += 1

    # Reward distinctively Chicago places.
    score += place.local_score / 5

    return score
def rank_places(places: list[Place],request: TripRequest,top_k: int = 15,) -> list[tuple[Place, float]]:
    """Rank places by request compatibility."""

    scored = [
        (
            place,
            score_place(
                place=place,
                request=request,
            ),
        )
        for place in places
    ]

    scored.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    return scored[:top_k]

def retrieve_places(repository: PlaceRepository, request: TripRequest, top_k: int=15,) -> list[Place]:
    """Retrieve the highest scoring places for a trip"""
    ranked = rank_places(
        places=repository.all(),
        request=request,
        top_k=top_k,
    )
    return [place for place, _ in ranked]