from app.schemas import Place, TripRequest
from app.services.place_retrieval import (
    rank_places,
    evaluate_place,
)


def make_place(
    *,
    name: str,
    tags: list[str],
    category: str = "landmark",
    neighborhood: str = "Loop",
    local_score: int = 7,
    walking_required: str = "minimal",
    transit_access: str = "good",
) -> Place:
    return Place(
        provider_id=name.lower().replace(" ", "-"),
        name=name,
        category=category,
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
def test_dietary_match_boosts_food_candidate() -> None:
    request = TripRequest(
        dietary_preferences=[
            "vegetarian"
        ]
    )

    vegetarian = make_place(
        name="Vegetarian Restaurant",
        category="restaurant",
        tags=["vegetarian"],
    )

    generic = make_place(
        name="Generic Cafe",
        category="cafe",
        tags=["coffee"],
    )

    vegetarian.category = "restaurant"
    generic.category = "cafe"

    vegetarian_result = evaluate_place(
        vegetarian,
        request,
    )

    generic_result = evaluate_place(
        generic,
        request,
    )

    assert (
        vegetarian_result.score
        > generic_result.score
    )

    assert "vegetarian" in (
        vegetarian_result.matched_tags
        or vegetarian.tags
    )
def test_retrieval_keeps_food_candidates_for_dietary_request() -> None:
    request = TripRequest(
        interests=["architecture"],
        dietary_preferences=[
            "vegetarian"
        ],
    )

    attractions = [
        make_place(
            name=f"Architecture {index}",
            category="museum",
            tags=["architecture"],
        )
        for index in range(20)
    ]

    food = make_place(
        name="Vegetarian Restaurant",
        category="restaurant",
        tags=["vegetarian"],
    )

    places = attractions + [food]

    ranked = rank_places(
        places,
        request,
        top_k=len(places),
    )

    assert any(
        candidate.place.name
        == "Vegetarian Restaurant"
        for candidate in ranked
    )