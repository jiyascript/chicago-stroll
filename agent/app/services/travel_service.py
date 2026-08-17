"""Travel time estimation utilities"""
from math import radians, sin, cos, sqrt, atan2
from app.schemas import Place

EARTH_RADIUS_KM = 6371.0

def distance_km(origin: Place,destination: Place,) -> float:
    """Return great-circle distance."""

    lat1 = radians(origin.latitude)
    lon1 = radians(origin.longitude)

    lat2 = radians(destination.latitude)
    lon2 = radians(destination.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    return EARTH_RADIUS_KM * c


def estimate_travel_minutes(origin: Place,destination: Place,) -> int:
    """Estimate travel time inside Chicago."""

    distance = distance_km(
        origin,
        destination,
    )

    if distance < 0.6:
        return 10

    if distance < 1.5:
        return 20

    if distance < 4:
        return 30

    return 45