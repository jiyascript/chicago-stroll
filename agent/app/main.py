"""Run a multi-turn Chicago Stroll conversation."""

from app.graph import create_planner_graph
from app.schemas import TripRequest, DraftItinerary, RetrievedPlace


def main() -> None:
    """Demonstrate persistent LangGraph conversation state."""

    graph = create_planner_graph()

    config = {
        "configurable": {
            "thread_id": "demo-conversation-1",
        }
    }

    first_message = """
    My parents are visiting Chicago.
    We will start in Hyde Park at 11 AM and need to end near Union Station
    by 8 PM. We like architecture and vegetarian food.
    They cannot walk too much.
    Our total budget is $150.
    """

    first_result = graph.invoke(
        {
            "user_message": first_message,
        },
        config=config,
    )

    print("\n===== TURN 1 =====")
    print("Missing:", first_result.get("missing_fields"))
    print(
        "Question:",
        first_result.get("clarification_question"),
    )

    second_result = graph.invoke(
        {
            "user_message": "August 8, 2026.",
        },
        config=config,
    )

    print("\n===== TURN 2 =====")
    trip_request = TripRequest.model_validate(second_result["trip_request"])

    print(trip_request.model_dump_json(indent=2,))
    print("Missing:", second_result.get("missing_fields"))
    print(
        "Ready:",
        second_result.get("ready_for_research"),
    )
    retrieved = second_result.get(
        "retrieved_places",
        [],
    )

    print("\nTop candidates:")

    for candidate_data in retrieved[:5]:
        candidate = RetrievedPlace.model_validate(
            candidate_data
        )

        print(
            candidate.place.name,
            candidate.score,
        )
    draft= DraftItinerary.model_validate(second_result["draft_itinerary"])
    print("\n===== DRAFT ITINERARY =====")

    if draft is None:
        print("No itinerary generated.")
    else:
        print(draft.model_dump_json(indent=2))

if __name__ == "__main__":
    main()