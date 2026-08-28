from app.schemas import DraftItinerary, ResolvedItinerary, ResolvedItineraryStop, RetrievedPlace

def hydrate_itinerary(itinerary: DraftItinerary, candidates: list[RetrievedPlace]) -> ResolvedItinerary:
    lookup={c.candidate_id:c.place for c in candidates}
    stops=[]
    for stop in itinerary.stops:
        place=lookup.get(stop.candidate_id)
        if place is None: raise ValueError(f"Cannot hydrate itinerary: unknown candidate_id '{stop.candidate_id}'.")
        stops.append(ResolvedItineraryStop(place=place,arrival_time=stop.arrival_time,departure_time=stop.departure_time,reason=stop.reason))
    return ResolvedItinerary(title=itinerary.title,summary=itinerary.summary,stops=stops)
