from app.schemas import Place, TripRequest
from app.services.place_retrieval import (
    rank_places,
    evaluate_place,
)


def make_place(
    *,
    name: str,
    tags: list[str],
    neighborhood: str = "Loop",
    local_score: int = 7,
    walking_required: str = "minimal",
    transit_access: str = "good",
) -> Place:
    return Place(
        provider_id=name.lower().replace(" ", "-"),
        name=name,
        category="landmark",
        ambiance=["local"],
        neighborhood=neighborhood,
        description="Test place.",
        tags=tags,
        price_tier="free",
        typical_visit_minutes=60,
        best_time_of_day="any",
        indoor_outdoor="indoor",
        weather_suitability=["any"],
        walking_required=walking_required,
        transit_access=transit_access,
        group_friendly=["solo", "family", "friends"],
        opening_hours={},
        reservation_required=False,
        website=None,
        local_score=local_score,
        why_visit="Test reason.",
        address=None,
        longitude=-87.63,
        latitude=41.88,
        source_categories=[],
        source_opening_hours=None,
    )


def test_interest_match_increases_score() -> None:
    request = TripRequest(
        interests=["architecture"],
    )

    matching = make_place(
        name="Architecture Place",
        tags=["architecture", "history"],
    )

    unrelated = make_place(
        name="Food Place",
        tags=["food"],
    )

    assert evaluate_place(matching,request,).score > evaluate_place(unrelated,request,).score


def test_rank_places_orders_best_match_first() -> None:
    request = TripRequest(
        interests=["architecture"],
        preferred_neighborhoods=["Loop"],
        group_type="family",
    )

    best = make_place(
        name="Best Match",
        tags=["architecture"],
        neighborhood="Loop",
        local_score=10,
        transit_access="excellent",
    )

    weak = make_place(
        name="Weak Match",
        tags=["coffee"],
        neighborhood="Pilsen",
        local_score=4,
    )

    ranked = rank_places(
        [weak, best],
        request,
        top_k=2,
    )

    assert ranked[0].place.name == "Best Match"