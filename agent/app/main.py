"""Run a multi-turn Chicago Stroll conversation."""

from app.graph import create_planner_graph
from app.schemas import TripRequest


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


if __name__ == "__main__":
    main()