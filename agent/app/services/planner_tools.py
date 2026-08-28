"""Tools the planner agent can call to discover places and check travel"""
from pydantic import BaseModel, Field
from app.schemas import Place, RetrievedPlace, TripRequest
from app.services.place_retrieval import rank_places
from app.services.travel_service import estimate_travel_minutes

class SearchPlaces(BaseModel):
    interests: list[str] = Field(default_factory=list)
    neighborhood: str | None = None
    dietary: list[str] = Field(default_factory= list)
    limit: int = 8
class GetTravelTime(BaseModel):
    from_candidate_id: str
    to_candidate_id: str


def run_search(repository, request: TripRequest, args: SearchPlaces, registry: list[dict],) -> tuple[str, list[dict]]:
    """Filter + score and assign stable IDs, merge"""
    pool = repository.all()
    if args.neighborhood:
        pool = [p for p in pool if p.neighborhood.lower() == args.neighborhood.lower()]
    if args.category:
        pool = [p for p in pool if p.category == args.category]

    ranked = rank_places(places = pool, request = request, top_k=args.limit)
    known = {c["place"]["provider_id"] for c in registry}
    for cand in ranked:
        pid = cand.place.provider_id
        if pid is known:
            if pid in known:
                continue
            cand.candidate_id= f"C{len(registry)+1}"
            registry.append(cand.model_dump(mode="json"))
            known.add(pid)

    lines = [
        f'{c["candidate_id"]}: {c["place"]["name"]} '
        f'({c["place"]["neighborhood"]}, {c["place"]["category"]}) '
        f'score={c["score"]:.1f}'
        for c in registry
    ]
    return "Known candidates:\n" + "\n".join(lines), registry


def run_travel(registry: list[dict], args: GetTravelTime) -> str:
    by_id = {c["candidate_id"]: c for c in registry}
    a, b = by_id.get(args.from_candidate_id), by_id.get(args.to_candidate_id)
    if not a or not b:
        return "Unknown candidate id — search first."
    minutes = estimate_travel_minutes(
        Place.model_validate(a["place"]),
        Place.model_validate(b["place"]),
    )
    return f"{args.from_candidate_id} → {args.to_candidate_id}: ~{minutes} min"