from app.schemas import RawPlace
from app.services.dataset_builder import (deduplicate_places,filter_candidates)


def test_deduplicate_places_merges_duplicate_records() -> None:
    first = RawPlace(
        provider_id="same-id",
        name="Example Museum",
        address="123 State St",
        neighborhood="Loop",
        provider_categories=["entertainment.museum"],
        longitude=-87.63,
        latitude=41.88,
        website=None,
        opening_hours=None,
        is_free=None,
    )

    second = RawPlace(
        provider_id="same-id",
        name="Example Museum",
        address="123 State St",
        neighborhood="Loop",
        provider_categories=[
            "entertainment",
            "no_fee",
        ],
        longitude=-87.63,
        latitude=41.88,
        website="https://example.com",
        opening_hours="Mo-Fr 10:00-17:00",
        is_free=True,
    )

    result = deduplicate_places(
        [first, second]
    )

    assert len(result) == 1

    merged = result[0]

    assert merged.website == "https://example.com"
    assert merged.opening_hours == "Mo-Fr 10:00-17:00"
    assert merged.is_free is True

    assert set(merged.provider_categories) == {
        "entertainment",
        "entertainment.museum",
        "no_fee",
    }
    def test_filter_candidates_removes_generic_places() -> None:
        places = [
            RawPlace(
                provider_id="1",
                name="Starbucks",
                neighborhood="Loop",
                provider_categories=["catering.cafe"],
                longitude=-87.63,
                latitude=41.88,
            ),
            RawPlace(
                provider_id="2",
                name="Independent Chicago Cafe",
                neighborhood="Pilsen",
                provider_categories=["catering.cafe"],
                longitude=-87.66,
                latitude=41.86,
            ),
        ]

        result = filter_candidates(places)

        assert len(result) == 1
        assert result[0].name == "Independent Chicago Cafe"