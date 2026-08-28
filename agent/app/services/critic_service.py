from datetime import datetime
from math import radians,sin,cos,sqrt,atan2
from app.schemas import CritiqueResult, DraftItinerary, RetrievedPlace, TripRequest

def _mins(t:str)->int:
    h,m=map(int,t.split(":")); return h*60+m

def _distance_minutes(a,b)->int:
    R=6371; p1,p2=radians(a.latitude),radians(b.latitude); dp=p2-p1; dl=radians(b.longitude-a.longitude)
    x=sin(dp/2)**2+cos(p1)*cos(p2)*sin(dl/2)**2; km=R*2*atan2(sqrt(x),sqrt(1-x))
    return max(5,round(km/4.5*60))

def critique_itinerary(request: TripRequest, itinerary: DraftItinerary, candidates: list[RetrievedPlace]) -> CritiqueResult:
    issues=[]; warnings=[]; lookup={c.candidate_id:c.place for c in candidates}
    for stop in itinerary.stops:
        p=lookup.get(stop.candidate_id)
        if p is None: issues.append(f"Unknown candidate_id: {stop.candidate_id}"); continue
        dur=_mins(stop.departure_time)-_mins(stop.arrival_time)
        if dur<=0: issues.append(f"Invalid time interval for {p.name}.")
        if abs(dur-p.typical_visit_minutes)>max(45,p.typical_visit_minutes): issues.append(f"Visit duration for {p.name} differs substantially from canonical duration.")
    for cur,nxt in zip(itinerary.stops,itinerary.stops[1:]):
        a,b=lookup.get(cur.candidate_id),lookup.get(nxt.candidate_id)
        if not a or not b: continue
        available=_mins(nxt.arrival_time)-_mins(cur.departure_time); required=_distance_minutes(a,b)
        if available<required: issues.append(f"Insufficient travel time between {a.name} and {b.name}: {available} minutes available, approximately {required} required.")
    if request.start_time and itinerary.stops and _mins(itinerary.stops[0].arrival_time)<_mins(request.start_time): issues.append("Itinerary starts before requested start time.")
    if request.end_time and itinerary.stops and _mins(itinerary.stops[-1].departure_time)>_mins(request.end_time): issues.append("Itinerary ends after requested end time.")
    if request.dietary_preferences:
        food=[lookup.get(s.candidate_id) for s in itinerary.stops]; food=[p for p in food if p and p.category in {"restaurant","cafe"}]
        if not food: warnings.append("No food stop is included despite dietary preferences.")
    return CritiqueResult(is_valid=not issues,issues=issues,warnings=warnings)
