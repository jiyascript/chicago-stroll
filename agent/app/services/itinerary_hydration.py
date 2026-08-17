"""Resolve itinerary provider IDs into canonical Place records."""

from app.schemas import DraftItinerary,ResolvedItinerary,ResolvedItineraryStop,RetrievedPlace


def hydrate_itinerary(itinerary: DraftItinerary,candidates: list[RetrievedPlace],) -> ResolvedItinerary:
    """Resolve itinerary stops against canonical retrieved candidates."""

    candidate_lookup = {
        candidate.candidate_id: candidate.place
        for candidate in candidates
    }

    resolved_stops: list[ResolvedItineraryStop] = []

    for stop in itinerary.stops:
        place = candidate_lookup.get(
            stop.candidate_id
        )

        if place is None:
            raise ValueError(
                (
                    "Cannot hydrate itinerary: unknown "
                    f"provider_id '{stop.candidate_id}'."
                )
            )

        resolved_stops.append(
            ResolvedItineraryStop(
                place=place,
                arrival_time=stop.arrival_time,
                departure_time=stop.departure_time,
                reason=stop.reason,
            )
        )

    return ResolvedItinerary(
        title=itinerary.title,
        summary=itinerary.summary,
        stops=resolved_stops,
    )