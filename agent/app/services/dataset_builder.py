import json
from pathlib import Path
from app.schemas import RawPlace, Place
from app.services.geoapify import normalize_place, search_places
from app.services.place_enrichment import enrich_place
from app.services.place_builder import build_place
from app.services.enrichment_cache import (cache_place, load_enrichment_cache)

CHICAGO_LONGITUDE = -87.6298
CHICAGO_LATITUDE = 41.8781
DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "chicago_places.generated.json"
)
SEARCH_CATEGORIES = [
    "entertainment.museum",
    "leisure.park",
    "tourism.sights",
    "catering.restaurant",
    "catering.cafe",
]
EXCLUDED_NAMES = {
    "starbucks",
    "corner bakery",
    "barnes & noble cafe",
}


def filter_candidates(
    places: list[RawPlace],
) -> list[RawPlace]:
    """Remove low-value or generic candidates before LLM enrichment."""

    filtered: list[RawPlace] = []

    for place in places:
        normalized_name = place.name.strip().lower()

        if normalized_name in EXCLUDED_NAMES:
            print(f"Filtering generic place: {place.name}")
            continue

        if not place.neighborhood:
            print(f"Filtering place without neighborhood: {place.name}")
            continue

        if not place.provider_categories:
            print(f"Filtering place without categories: {place.name}")
            continue

        filtered.append(place)

    removed = len(places) - len(filtered)

    print("\nFiltering candidates...")
    print(f"Removed {removed} low-value candidates.")
    print(f"{len(filtered)} candidates remain.")

    return filtered
def search_all_categories() -> list[RawPlace]:
    """Collect normalized raw places from every configured category."""

    places: list[RawPlace] = []

    for category in SEARCH_CATEGORIES:
        print(f"Searching {category}...")

        features = search_places(
            categories=[category],
            longitude=CHICAGO_LONGITUDE,
            latitude=CHICAGO_LATITUDE,
            radius_meters=15_000,
            limit=10,
        )

        print(f"Found {len(features)} results.")

        for feature in features:
            try:
                place = normalize_place(feature)
            except ValueError as exc:
                print(f"Skipping invalid result: {exc}")
                continue

            places.append(place)

    return places
from app.schemas import Place, RawPlace
from app.services.place_builder import build_place
from app.services.place_enrichment import enrich_place


def enrich_places(
    places: list[RawPlace],
) -> list[Place]:
    """Enrich places while resuming previously completed work."""

    cache = load_enrichment_cache()

    final_places: list[Place] = []

    total = len(places)

    for index, raw_place in enumerate(
        places,
        start=1,
    ):
        cached = cache.get(
            raw_place.provider_id
        )

        if cached is not None:
            print(
                f"Cached {index}/{total}: "
                f"{raw_place.name}"
            )

            final_places.append(
                Place.model_validate(cached)
            )

            continue

        print(
            f"Enriching {index}/{total}: "
            f"{raw_place.name}"
        )

        try:
            enrichment = enrich_place(
                raw_place
            )

            place = build_place(
                raw_place=raw_place,
                enrichment=enrichment,
            )

        except Exception as exc:
            message = str(exc)

            if (
                "RESOURCE_EXHAUSTED" in message
                or "429" in message
            ):
                print("\nGemini quota exhausted.")
                print(
                    "Progress has been saved. "
                    "Run the builder again when quota is available."
                )
                break

            print(
                f"Failed {raw_place.name}: {exc}"
            )
            continue

        final_places.append(place)

        cache_place(
            cache,
            place,
        )

    print(
        f"\nAvailable final places: "
        f"{len(final_places)}/{total}"
    )

    return final_places
def deduplicate_places(places: list[RawPlace],) -> list[RawPlace]:
    """Deduplicate places by provider ID and merge complementary fields."""
    consolidated: dict[str, RawPlace] = {}

    for place in places:
        existing = consolidated.get(place.provider_id)

        if existing is None:
            consolidated[place.provider_id] = place
            continue

        merged_categories = sorted(
            set(existing.provider_categories)
            | set(place.provider_categories)
        )

        merged_place = RawPlace(
            provider_id=existing.provider_id,
            name=existing.name or place.name,
            address=existing.address or place.address,
            neighborhood=existing.neighborhood or place.neighborhood,
            provider_categories=merged_categories,
            longitude=existing.longitude,
            latitude=existing.latitude,
            website=existing.website or place.website,
            opening_hours=existing.opening_hours or place.opening_hours,
            is_free=(
                existing.is_free
                if existing.is_free is not None
                else place.is_free
            ),
        )

        consolidated[place.provider_id] = merged_place

    unique_places = list(consolidated.values())
    removed_count = len(places) - len(unique_places)

    print("\nConsolidating duplicate places...")
    print(f"Removed {removed_count} duplicate records.")
    print(f"{len(unique_places)} unique places remain.")

    return unique_places

def save_dataset(places: list[Place],) -> None:
    """Write validated Chicago places to the generated dataset."""

    DATASET_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = [
        place.model_dump(mode="json")
        for place in places
    ]

    DATASET_PATH.write_text(
        json.dumps(
            payload,
            indent=2,
        )
    )

    print(
        f"\nSaved {len(places)} places to "
        f"{DATASET_PATH}"
    )

def build_dataset() -> None:
    """Build the complete Chicago places dataset."""

    raw_places = search_all_categories()

    print(f"\nCollected {len(raw_places)} raw places.")

    unique_places = deduplicate_places(raw_places)

    candidate_places = filter_candidates(
        unique_places
    )

    final_places = enrich_places(
        candidate_places
    )
    save_dataset(
        final_places
    )

    print("\nSample final places:")

    for place in final_places[:5]:
        print(
            f"- {place.name} "
            f"[{place.category}] "
            f"({place.neighborhood})"
        )
