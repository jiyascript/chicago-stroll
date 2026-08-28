from app.schemas import *
from app.services.agent_tools import SearchPlaces,run_search
class FakeProvider:
    def search(self,**kwargs):
        return [RawPlace(provider_id="p1",name="Museum",provider_categories=["entertainment.museum"],longitude=-87.63,latitude=41.88)]
def test_live_search_populates_registry():
    out,registry=run_search(FakeProvider(),TripRequest(interests=["museum"]),SearchPlaces(place_types=["museum"], anchor="Loop", query_terms=["museum"]),[])
    assert len(registry)==1 and registry[0]["candidate_id"]=="C1"
