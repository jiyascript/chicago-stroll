from app.schemas import *
from app.services.itinerary_hydration import hydrate_itinerary

def test_hydration():
    p=Place(provider_id="x",name="X",latitude=41.88,longitude=-87.63); c=RetrievedPlace(candidate_id="C1",place=p)
    d=DraftItinerary(title="T",summary="S",stops=[ItineraryStop(candidate_id="C1",arrival_time="11:00",departure_time="12:00",reason="R")])
    assert hydrate_itinerary(d,[c]).stops[0].place.name=="X"
