"""Tests for the PlaceRepository."""

import json

from app.repositories import PlaceRepository
from app.schemas import Place


def make_place(
    provider_id: str,
    name: str,
    category: str,
    neighborhood: str,
    tags: list[str],
) -> Place:
    """Create a valid place for repository tests."""

    return Place(
        provider_id=provider_id,
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
        walking_required="minimal",
        transit_access="good",
        group_friendly=["solo", "friends"],
        opening_hours={},
        reservation_required=False,
        website=None,
        local_score=7,
        why_visit="Useful test place.",
        address=None,
        longitude=-87.63,
        latitude=41.88,
        source_categories=[],
        source_opening_hours=None,
    )


def test_repository_queries_places(tmp_path) -> None:
    places = [
        make_place(
            "1",
            "Architecture Museum",
            "museum",
            "Loop",
            ["architecture", "history"],
        ),
        make_place(
            "2",
            "Hyde Park Books",
            "bookstore",
            "Hyde Park",
            ["books", "local"],
        ),
    ]

    dataset_path = tmp_path / "places.json"

    dataset_path.write_text(
        json.dumps(
            [
                place.model_dump(mode="json")
                for place in places
            ]
        )
    )

    repository = PlaceRepository(
        dataset_path=dataset_path
    )

    assert len(repository.all()) == 2
    assert repository.get_by_id("1").name == "Architecture Museum"

    assert len(
        repository.find_by_category("museum")
    ) == 1

    assert len(
        repository.find_by_neighborhood("Hyde Park")
    ) == 1

    assert len(
        repository.find_by_tags(["architecture"])
    ) == 1