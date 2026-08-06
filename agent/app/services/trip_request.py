"""Update requests"""
from app.schemas import TripRequest, TripRequestUpdate

def merge_trip_request(
        current:TripRequest, update:TripRequestUpdate) -> TripRequest:
    current_data = current.model_dump()
    update_data = update.model_dump(
        exclude_none=True
    )
    merged_data = {
        **current_data,
        **update_data
    }
    return TripRequest.model_validate(merged_data)