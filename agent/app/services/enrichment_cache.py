"""Persistent cache for place enrichment results."""

import json
from pathlib import Path

from app.schemas import Place


CACHE_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "enrichment_cache.json"
)


def load_enrichment_cache() -> dict[str, dict]:
    """Load previously completed place records."""

    if not CACHE_PATH.exists():
        return {}

    contents = CACHE_PATH.read_text().strip()

    if not contents:
        return {}

    try:
        return json.loads(contents)
    except json.JSONDecodeError:
        return {}


def save_enrichment_cache(
    cache: dict[str, dict],
) -> None:
    """Persist completed place records."""

    CACHE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    CACHE_PATH.write_text(
        json.dumps(
            cache,
            indent=2,
            default=str,
        )
    )


def cache_place(
    cache: dict[str, dict],
    place: Place,
) -> None:
    """Add a successfully built place to the cache."""

    cache[place.provider_id] = place.model_dump(
        mode="json"
    )

    save_enrichment_cache(cache)