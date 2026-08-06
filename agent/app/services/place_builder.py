from app.schemas import Place, PlaceEnrichment, RawPlace

def build_place(raw_place: RawPlace, enrichment: PlaceEnrichment) -> Place:
    price_tier = enrichment.price_tier
    if raw_place.is_free is True:
        price_tier = "free"

    weather_suitability = enrichment.weather_suitability

    # "any" already represents all weather conditions.
    if "any" in weather_suitability:
        weather_suitability = ["any"]

    return Place(
        provider_id=raw_place.provider_id,
        name=raw_place.name,
        category=enrichment.category,
        ambiance=enrichment.ambiance,
        neighborhood=raw_place.neighborhood or "Unknown",
        address=raw_place.address,
        longitude=raw_place.longitude,
        latitude=raw_place.latitude,
        description=enrichment.description,
        tags=enrichment.tags,
        price_tier=price_tier,
        typical_visit_minutes=enrichment.typical_visit_minutes,
        best_time_of_day=enrichment.best_time_of_day,
        indoor_outdoor=enrichment.indoor_outdoor,
        weather_suitability=weather_suitability,
        walking_required=enrichment.walking_required,
        transit_access=enrichment.transit_access,
        group_friendly=enrichment.group_friendly,
        opening_hours={},
        source_opening_hours=raw_place.opening_hours,
        source_categories=raw_place.provider_categories,
        reservation_required=enrichment.reservation_required,
        website=raw_place.website,
        local_score=enrichment.local_score,
        why_visit=enrichment.why_visit,
    )

