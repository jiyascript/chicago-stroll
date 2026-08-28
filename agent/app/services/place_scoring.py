from app.schemas import Place, RawPlace, RetrievedPlace, TripRequest

def raw_to_place(raw: RawPlace) -> Place:
    cats=[x.lower() for x in raw.provider_categories]
    category="restaurant" if any("catering.restaurant" in x for x in cats) else "cafe" if any("catering.cafe" in x for x in cats) else "park" if any("leisure.park" in x for x in cats) else "museum" if any("museum" in x for x in cats) else "attraction"
    tags=sorted({seg for cat in cats for seg in cat.replace("-","_").split(".") if seg})
    return Place(provider_id=raw.provider_id,name=raw.name,category=category,neighborhood=raw.neighborhood or "Chicago",description="Live Geoapify place result.",tags=tags,price_tier="free" if raw.is_free else "unknown",typical_visit_minutes=60 if category in {"museum","restaurant"} else 30,indoor_outdoor="outdoor" if category=="park" else "mixed",walking_required="minimal",transit_access="good",opening_hours=raw.opening_hours,website=raw.website,local_score=5,why_visit="Live candidate matching the current search.",address=raw.address,longitude=raw.longitude,latitude=raw.latitude,source_categories=raw.provider_categories,source_opening_hours=raw.opening_hours)

def score_place(place: Place, request: TripRequest, query_terms: list[str]) -> RetrievedPlace:
    requested={x.lower() for x in request.interests+request.dietary_preferences+query_terms}
    tags={x.lower() for x in place.tags}|{place.category.lower(),place.name.lower()}
    matches=sorted(x for x in requested if any(x in t or t in x for t in tags))
    score=5*len(matches)+place.local_score/5
    if place.neighborhood.lower() in {x.lower() for x in request.preferred_neighborhoods}: score+=3
    if place.neighborhood.lower() in {x.lower() for x in request.excluded_neighborhoods}: score-=100
    return RetrievedPlace(place=place,score=score,matched_tags=matches,retrieval_reasons=[f"Matches: {', '.join(matches)}"] if matches else ["Live search candidate"])
