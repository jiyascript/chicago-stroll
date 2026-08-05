from app.config import create_model
from app.schemas import TripRequest

SAMPLE_REQUEST = """
Plan a relaxed Chicago day from 10 AM to 7 PM.
I like bookstores, art, and quiet places.
I am vegetarian, and my total budget is $70.
"""
def main() -> None:
    model= create_model()
    structured_model = model.with_structured_output(TripRequest) #use this model, but require its answer to follow the TripRequest schema
    trip_request = structured_model.invoke(SAMPLE_REQUEST)

    print(trip_request.model_dump_json(indent=2))

if __name__ == "__main__":
    main()