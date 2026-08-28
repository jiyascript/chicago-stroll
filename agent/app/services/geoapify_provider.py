"""Live Geoapify provider with narrow, testable methods."""
import os
from datetime import datetime
import httpx
from app.config import load_environment
from app.schemas import RawPlace

PLACES_URL = "https://api.geoapify.com/v2/places"
DETAILS_URL = "https://api.geoapify.com/v2/place-details"
GEOCODE_URL = "https://api.geoapify.com/v1/geocode/search"
ROUTING_URL = "https://api.geoapify.com/v1/routing"

class GeoapifyProvider:
    def __init__(self, api_key: str | None = None, client: httpx.Client | None = None):
        load_environment()
        self.api_key = api_key or os.getenv("GEOAPIFY_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEOAPIFY_API_KEY is missing from the environment.")
        self.client = client or httpx.Client(timeout=20.0)

    def geocode(self, text: str) -> tuple[float, float]:
        q = text if "Chicago" in text else f"{text}, Chicago, IL"
        r = self.client.get(GEOCODE_URL, params={"text":q,"limit":1,"apiKey":self.api_key})
        r.raise_for_status(); features=r.json().get("features",[])
        if not features: raise ValueError(f"Could not geocode '{text}'.")
        lon, lat = features[0]["geometry"]["coordinates"]
        return float(lat), float(lon)
    def find_place(self, text: str) -> RawPlace | None:
        q = text if "Chicago" in text else f"{text}, Chicago, IL"

        r = self.client.get(
            GEOCODE_URL,
            params={
                "text": q,
                "limit": 1,
                "apiKey": self.api_key,
            },
        )
        r.raise_for_status()

        features = r.json().get("features", [])

        if not features:
            return None

        feature = features[0]
        p = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [])

        if len(coords) != 2 or not p.get("place_id"):
            return None

        name = p.get("name")

        # Avoid treating a city/neighborhood result as a named POI.
        if not name:
            return None

        return RawPlace(
            provider_id=p["place_id"],
            name=name,
            address=p.get("formatted"),
            neighborhood=p.get("suburb") or p.get("district"),
            provider_categories=p.get("categories") or [],
            longitude=float(coords[0]),
            latitude=float(coords[1]),
            website=p.get("website"),
            opening_hours=p.get("opening_hours"),
            is_free=None,
        )
    def search(self, *, categories: list[str], anchor: str, radius_meters: int = 5000, limit: int = 12) -> list[RawPlace]:
        lat, lon = self.geocode(anchor)
        params={"categories":",".join(categories),"filter":f"circle:{lon},{lat},{radius_meters}","bias":f"proximity:{lon},{lat}","limit":limit,"apiKey":self.api_key}
        r=self.client.get(PLACES_URL,params=params); r.raise_for_status()
        out=[]
        for f in r.json().get("features",[]):
            try: out.append(self._normalize(f))
            except ValueError: continue
        return out

    def details(self, place_id: str) -> dict:
        r=self.client.get(DETAILS_URL,params={"id":place_id,"apiKey":self.api_key}); r.raise_for_status()
        features=r.json().get("features",[])
        return features[0].get("properties",{}) if features else {}

    def travel(self, *, origin: tuple[float,float], destination: tuple[float,float], mode: str="walk") -> dict:
        olat,olon=origin; dlat,dlon=destination
        r=self.client.get(ROUTING_URL,params={"waypoints":f"{olat},{olon}|{dlat},{dlon}","mode":mode,"apiKey":self.api_key}); r.raise_for_status()
        features=r.json().get("features",[])
        props=features[0].get("properties",{}) if features else {}
        legs=props.get("legs",[]) or []
        seconds=sum(float(x.get("time",0)) for x in legs)
        meters=sum(float(x.get("distance",0)) for x in legs)
        return {"minutes":round(seconds/60),"distance_meters":round(meters),"mode":mode}

    @staticmethod
    def _normalize(feature: dict) -> RawPlace:
        p=feature.get("properties",{}); coords=feature.get("geometry",{}).get("coordinates",[])
        if len(coords)!=2 or not p.get("name") or not p.get("place_id"): raise ValueError("Incomplete place")
        raw=(p.get("datasource") or {}).get("raw") or {}
        fee=raw.get("fee"); free=True if fee=="no" else False if fee=="yes" else None
        return RawPlace(provider_id=p["place_id"],name=p["name"],address=p.get("formatted"),neighborhood=p.get("suburb") or p.get("district"),provider_categories=p.get("categories",[]),longitude=float(coords[0]),latitude=float(coords[1]),website=p.get("website"),opening_hours=p.get("opening_hours"),is_free=free)

def opening_status(opening_hours: str | None, date: str, arrival_time: str) -> str:
    """Conservative evidence evaluator: never invents hours."""
    if not opening_hours:
        return "unknown"
    # Geoapify commonly returns OSM opening_hours syntax. Full OSM parsing is intentionally
    # not guessed here; preserve the evidence for the model and label it 'reported'.
    return "reported"
