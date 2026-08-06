"""Geoapify API client for Chicago Stroll."""

import os

import httpx
from app.schemas import RawPlace
from app.config import load_environment


load_environment()


GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"


def search_places(
    categories: list[str],
    longitude: float,
    latitude: float,
    radius_meters: int = 10_000,
    limit: int = 20,
) -> list[dict]:
    """Search Geoapify for places near a coordinate."""

    api_key = os.getenv("GEOAPIFY_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEOAPIFY_API_KEY is missing from the environment."
        )

    params = {
        "categories": ",".join(categories),
        "filter": (
            f"circle:{longitude},{latitude},{radius_meters}"
        ),
        "bias": f"proximity:{longitude},{latitude}",
        "limit": limit,
        "apiKey": api_key,
    }

    response = httpx.get(
        GEOAPIFY_PLACES_URL,
        params=params,
        timeout=20.0,
    )

    response.raise_for_status()

    payload = response.json()

    return payload.get("features", [])
def normalize_place(feature: dict) -> RawPlace:
    """Convert one Geoapify feature into normalized factual data."""

    properties = feature.get("properties", {})
    geometry = feature.get("geometry", {})
    coordinates = geometry.get("coordinates", [])

    if len(coordinates) != 2:
        raise ValueError("Geoapify result is missing coordinates.")

    name = properties.get("name")

    if not name:
        raise ValueError("Geoapify result is missing a place name.")

    provider_id = properties.get("place_id")

    if not provider_id:
        raise ValueError("Geoapify result is missing a place ID.")
    datasource = properties.get("datasource", {})
    raw_data = datasource.get("raw", {})

    fee_value = raw_data.get("fee")

    if fee_value == "no":
        is_free = True
    elif fee_value == "yes":
        is_free = False
    else:
        is_free = None
    return RawPlace(
        provider_id=provider_id,
        name=name,
        address=properties.get("formatted"),
        neighborhood=properties.get("suburb"),
        provider_categories=properties.get("categories", []),
        longitude=coordinates[0],
        latitude=coordinates[1],
        website=properties.get("website"),
        opening_hours=properties.get("opening_hours"),
        is_free=is_free,
    )