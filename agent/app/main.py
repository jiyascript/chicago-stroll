from langchain_core.messages import HumanMessage, SystemMessage
from app.config import create_model
from app.schemas import TripRequest
from app.prompts.intake import INTAKE_SYSTEM_PROMPT
from app.services.intake import find_missing_required_fields


SAMPLE_REQUEST = """
My parents are visiting Chicago this Saturday.
We will start in Hyde Park around 11 AM and need to end near Union Station
by 8 PM. We like architecture and vegetarian food. They cannot walk too much.
Our total budget is $150.
"""


def main() -> None:
    """Extract and display structured trip preferences."""

    model = create_model()
    structured_model = model.with_structured_output(TripRequest)

    trip_request = structured_model.invoke(
        [
            SystemMessage(content=INTAKE_SYSTEM_PROMPT),
            HumanMessage(content=SAMPLE_REQUEST),
        ]
    )

    print("\nStructured trip request:\n")
    print(trip_request.model_dump_json(indent=2))

missing_fields = find_missing_required_fields(trip_request)
print("\nMissing required fields:\n")
if missing_fields:
    for fname in missing_fields:
        print(f"- {fname}")
else:
    print("None")

    
if __name__ == "__main__":
    main()