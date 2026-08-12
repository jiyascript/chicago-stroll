"""Run a multi-turn Chicago Stroll conversation."""

from app.graph import create_planner_graph
from app.schemas import (
    DraftItinerary,
    RetrievedPlace,
    TripRequest,
)


FOOD_CATEGORIES = {
    "restaurant",
    "cafe",
}


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

    print(
        "Missing:",
        first_result.get("missing_fields"),
    )

    print(
        "Question:",
        first_result.get(
            "clarification_question"
        ),
    )

    second_result = graph.invoke(
        {
            "user_message": "August 8, 2026.",
        },
        config=config,
    )

    print("\n===== TURN 2 =====")

    trip_request = TripRequest.model_validate(
        second_result["trip_request"]
    )

    print(
        trip_request.model_dump_json(
            indent=2
        )
    )

    print(
        "Missing:",
        second_result.get(
            "missing_fields"
        ),
    )

    print(
        "Ready:",
        second_result.get(
            "ready_for_research"
        ),
    )

    retrieved_data = second_result.get(
        "retrieved_places",
        [],
    )

    retrieved_places = [
        RetrievedPlace.model_validate(
            candidate
        )
        for candidate in retrieved_data
    ]

    attractions = [
        candidate
        for candidate in retrieved_places
        if candidate.place.category
        not in FOOD_CATEGORIES
    ]

    food_options = [
        candidate
        for candidate in retrieved_places
        if candidate.place.category
        in FOOD_CATEGORIES
    ]

    print("\n===== TOP ATTRACTIONS =====")

    if not attractions:
        print("No attraction candidates retrieved.")
    else:
        for candidate in attractions[:5]:
            print(
                f"- {candidate.place.name}: "
                f"{candidate.score:.1f}"
            )

    print("\n===== FOOD OPTIONS =====")

    if not food_options:
        print("No food candidates retrieved.")
    else:
        for candidate in food_options[:5]:
            print(
                f"- {candidate.place.name}: "
                f"{candidate.score:.1f}"
            )

            if candidate.matched_tags:
                print(
                    "  Matches:",
                    ", ".join(
                        candidate.matched_tags
                    ),
                )

    print("\n===== DRAFT ITINERARY =====")

    draft_data = second_result.get(
        "draft_itinerary"
    )

    if draft_data is None:
        print("No itinerary generated.")
    else:
        draft = DraftItinerary.model_validate(
            draft_data
        )

        print(
            draft.model_dump_json(
                indent=2
            )
        )

    print("\n===== CRITIQUE =====")

    critique = second_result.get(
        "critique_result"
    )

    if critique is None:
        print("No critique generated.")
    else:
        print(critique)

    print(
        "\nRepair count:",
        second_result.get(
            "repair_count",
            0,
        ),
    )


if __name__ == "__main__":
    main()