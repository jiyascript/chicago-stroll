from app.schemas import *
from app.services.critic_service import critique_itinerary

def place(name,cid,lat=41.88,lon=-87.63):
    p=Place(provider_id=name,name=name,latitude=lat,longitude=lon,typical_visit_minutes=60)
    return RetrievedPlace(candidate_id=cid,place=p)
def test_unknown_candidate_rejected():
    d=DraftItinerary(title="x",summary="x",stops=[ItineraryStop(candidate_id="C99",arrival_time="11:00",departure_time="12:00",reason="x")])
    r=critique_itinerary(TripRequest(start_time="11:00",end_time="13:00",start_location="Loop"),d,[place("A","C1")])
    assert not r.is_valid and any("Unknown candidate_id" in x for x in r.issues)
