"""Tool schemas and deterministic executors for the planning agent."""
import json
from typing import Literal
from pydantic import BaseModel, Field
from app.schemas import DraftItinerary, RetrievedPlace, TripRequest
from app.services.geoapify_provider import GeoapifyProvider, opening_status
from app.services.place_scoring import raw_to_place, score_place

class SearchPlaces(BaseModel):
    """Search live Chicago places using semantic place types."""
    place_types: list[
        Literal[
            "attraction",
            "architecture",
            "museum",
            "restaurant",
            "cafe",
            "park",
            "shopping",
            "hotel",
        ]
    ] = Field(
        description=(
            "Semantic place types to search for. "
            "Use architecture for architecture-related attractions."
        )
    )

    anchor: str = Field(
        description="Chicago neighborhood, landmark, or address to search around"
    )

    query_terms: list[str] = Field(
        default_factory=list,
        description="User concepts used to rerank live results",
    )

    radius_meters: int = Field(default=5000, ge=500, le=15000)
    limit: int = Field(default=10, ge=1, le=20)
PLACE_TYPE_TO_CATEGORIES = {
    "attraction": ["tourism"],
    "architecture": ["tourism"],
    "museum": ["entertainment.museum"],
    "restaurant": ["catering.restaurant"],
    "cafe": ["commercial.cafe"],
    "park": ["leisure.park"],
    "shopping": ["commercial"],
    "hotel": ["accommodation.hotel"],
}
class FindPlace(BaseModel):
    """Find a specific named Chicago place or landmark."""

    query: str = Field(
        description=(
            "Specific place, landmark, museum, restaurant, or attraction "
            "to find by name, e.g. 'Chicago Cultural Center'."
        )
    )
class GetPlaceDetails(BaseModel):
    """Fetch richer live details for one discovered candidate."""
    candidate_id: str

class GetTravelTime(BaseModel):
    """Fetch live route duration between two discovered candidates."""
    origin_candidate_id: str
    destination_candidate_id: str
    mode: str = Field(default="walk", pattern="^(walk|bicycle|drive|transit)$")

class CheckHours(BaseModel):
    """Check opening-hours evidence for a discovered candidate at a proposed time."""
    candidate_id: str
    date: str
    arrival_time: str

TOOLS=[SearchPlaces,FindPlace,GetPlaceDetails,GetTravelTime,CheckHours,DraftItinerary]

def _lookup(registry: list[dict], cid: str) -> RetrievedPlace:
    for raw in registry:
        c=RetrievedPlace.model_validate(raw)
        if c.candidate_id==cid: return c
    raise ValueError(f"Unknown candidate_id: {cid}")

def run_search(provider: GeoapifyProvider, request: TripRequest, args: SearchPlaces, registry: list[dict]) -> tuple[str,list[dict]]:
    categories = []

    for place_type in args.place_types:
        categories.extend(PLACE_TYPE_TO_CATEGORIES[place_type])

    # Remove duplicates while preserving order.
    categories = list(dict.fromkeys(categories))

    query_terms = list(args.query_terms)

    # Architecture is not a Geoapify category itself, so preserve the
    # semantic intent for reranking.
    if "architecture" in args.place_types and "architecture" not in query_terms:
        query_terms.append("architecture")

    found = provider.search(
        categories=categories,
        anchor=args.anchor,
        radius_meters=args.radius_meters,
        limit=args.limit,
    )
    existing={RetrievedPlace.model_validate(x).place.provider_id:RetrievedPlace.model_validate(x) for x in registry}
    next_num=len(existing)+1
    for raw in found:
        if raw.provider_id in existing: continue
        c=score_place(raw_to_place(raw),request,query_terms)
        c.candidate_id=f"C{next_num}"; next_num+=1; existing[raw.provider_id]=c
    ranked=sorted(existing.values(),key=lambda x:x.score,reverse=True)
    new=[c.model_dump(mode="json") for c in ranked]
    compact=[{"candidate_id":c.candidate_id,"name":c.place.name,"category":c.place.category,"neighborhood":c.place.neighborhood,"address":c.place.address,"score":round(c.score,2),"opening_hours":c.place.source_opening_hours} for c in ranked[:args.limit]]
    return json.dumps(compact,ensure_ascii=False),new
def run_find(
    provider: GeoapifyProvider,
    request: TripRequest,
    args: FindPlace,
    registry: list[dict],
) -> tuple[str, list[dict]]:
    found = provider.find_place(args.query)

    if found is None:
        return json.dumps(
            {"found": False, "query": args.query},
            ensure_ascii=False,
        ), registry

    existing = {
        RetrievedPlace.model_validate(x).place.provider_id:
        RetrievedPlace.model_validate(x)
        for x in registry
    }

    if found.provider_id not in existing:
        candidate = score_place(
            raw_to_place(found),
            request,
            [args.query],
        )

        candidate.candidate_id = f"C{len(existing) + 1}"
        existing[found.provider_id] = candidate

    ranked = sorted(
        existing.values(),
        key=lambda x: x.score,
        reverse=True,
    )

    new_registry = [
        candidate.model_dump(mode="json")
        for candidate in ranked
    ]

    matched = existing[found.provider_id]

    result = {
        "found": True,
        "candidate_id": matched.candidate_id,
        "name": matched.place.name,
        "address": matched.place.address,
        "category": matched.place.category,
    }

    return json.dumps(result, ensure_ascii=False), new_registry
def run_details(provider: GeoapifyProvider, registry: list[dict], args: GetPlaceDetails) -> str:
    c=_lookup(registry,args.candidate_id); details=provider.details(c.place.provider_id)
    allowed={k:details.get(k) for k in ["name","formatted","website","opening_hours","categories","contact"] if details.get(k) is not None}
    return json.dumps(allowed,ensure_ascii=False)

def run_travel(provider: GeoapifyProvider, registry: list[dict], args: GetTravelTime) -> str:
    a=_lookup(registry,args.origin_candidate_id).place; b=_lookup(registry,args.destination_candidate_id).place
    return json.dumps(provider.travel(origin=(a.latitude,a.longitude),destination=(b.latitude,b.longitude),mode=args.mode))

def run_hours(provider: GeoapifyProvider, registry: list[dict], args: CheckHours) -> str:
    c=_lookup(registry,args.candidate_id); details=provider.details(c.place.provider_id)
    hours=details.get("opening_hours") or c.place.source_opening_hours
    return json.dumps({"status":opening_status(hours,args.date,args.arrival_time),"opening_hours_evidence":hours})
