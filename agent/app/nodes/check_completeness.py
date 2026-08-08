from app.schemas import TripRequest
from app.services.intake import find_missing_required_fields
from app.state import PlannerState


def check_completeness(state: PlannerState) -> dict:
    """Find required planning fields that are still missing."""

    trip_request_data = state.get("trip_request")

    if trip_request_data is None:
        raise ValueError(
            "trip_request must exist before checking completeness."
        )

    trip_request = TripRequest.model_validate(
        trip_request_data
    )

    missing_fields = find_missing_required_fields(
        trip_request
    )

    return {"missing_fields": missing_fields,}