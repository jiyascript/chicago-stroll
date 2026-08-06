"""Run the Chicago Stroll planner."""

from app.graph import create_planner_graph


SAMPLE_REQUEST = """
My parents are visiting Chicago on August 8, 2026.
We will start in Hyde Park around 11 AM and need to end near Union Station
by 8 PM. We like architecture and vegetarian food.
They cannot walk too much.
Our total budget is $150.
"""


def main() -> None:
    """Run the planner workflow."""

    graph = create_planner_graph()

    initial_state = {
        "user_message": SAMPLE_REQUEST,
        "trip_request": None,
        "missing_fields": [],
        "clarification_question": None,
        "ready_for_research": False,
    }

    final_state = graph.invoke(initial_state)

    print("\n===== FINAL STATE =====\n")
    print(final_state["trip_request"].model_dump_json(indent=2))
    print("\nMissing Fields:")
    print(final_state["missing_fields"])
    print("\nClarification Question:")
    print(final_state.get("clarification_question"))
    print("\nReady For Research:")
    print(final_state.get("ready_for_research",False))


if __name__ == "__main__":
    main()