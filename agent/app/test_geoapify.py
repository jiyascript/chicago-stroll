"""Temporarily test Geoapify normalization and LLM enrichment."""
from app.services.place_builder import build_place
from app.services.geoapify import (
    normalize_place,
    search_places,
)
from app.services.place_enrichment import enrich_place


def main() -> None:
    """Search, normalize, and enrich one Chicago place."""

    results = search_places(
        categories=["entertainment.museum"],
        longitude=-87.6298,
        latitude=41.8781,
        radius_meters=12_000,
        limit=5,
    )

    raw_place = normalize_place(results[0])
    enrichment = enrich_place(raw_place)

    print("\nRAW PLACE:\n")
    print(raw_place.model_dump_json(indent=2))

    print("\nENRICHMENT:\n")
    print(enrichment.model_dump_json(indent=2))
    place = build_place(
        raw_place=raw_place,
        enrichment=enrichment,
    )

    print("\nFINAL PLACE:\n")
    print(place.model_dump_json(indent=2))

if __name__ == "__main__":
    main()