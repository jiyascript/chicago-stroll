"""Run a multi-turn Chicago Stroll conversation."""

from app.graph import create_planner_graph
from app.schemas import (
    DraftItinerary,
    RetrievedPlace,
    TripRequest,
)
from app.services.itinerary_hydration import hydrate_itinerary
from app.services.travel_service import estimate_travel_minutes

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
        print(
            "No food candidates retrieved."
        )
    else:
        for candidate in food_options[:5]:
            print(
                f"- {candidate.place.name}: "
                f"{candidate.score:.1f}"
            )

            print(
                "  Tags:",
                candidate.place.tags,
            )

            print(
                "  Matched:",
                candidate.matched_tags,
            )

    draft_data = second_result.get(
        "draft_itinerary"
    )

    print("\n===== FINAL ITINERARY =====")

    if draft_data is None:
        print(
            "No itinerary generated."
        )
    else:
        draft = DraftItinerary.model_validate(
            draft_data
        )

        resolved = hydrate_itinerary(
            itinerary=draft,
            candidates=retrieved_places,
        )

        print(
            f"\n{resolved.title}"
        )

        print(
            resolved.summary
        )

        for stop in resolved.stops:
            print(
                (
                    f"\n{stop.arrival_time}"
                    f" - "
                    f"{stop.departure_time}"
                )
            )

            print(
                stop.place.name
            )

            print(
                f"Category: "
                f"{stop.place.category}"
            )

            print(
                f"Neighborhood: "
                f"{stop.place.neighborhood}"
            )

            print(
                f"Typical visit: "
                f"{stop.place.typical_visit_minutes} min"
            )

            print(
                f"Reason: "
                f"{stop.reason}"
            )
    print("\n===== TRAVEL ESTIMATES =====")

    for current, next_stop in zip(
        resolved.stops,
        resolved.stops[1:],
    ):
        minutes = estimate_travel_minutes(
            current.place,
            next_stop.place,
        )

        print(
            f"- {current.place.name} "
            f"→ {next_stop.place.name}: "
            f"~{minutes} min"
        )

    print("\n===== CRITIQUE =====")

    critique = second_result.get(
        "critique_result"
    )

    if critique is None:
        print(
            "No critique generated."
        )
    else:
        print(
            critique
        )

    print(
        "\nRepair count:",
        second_result.get(
            "repair_count",
            0,
        ),
    )


if __name__ == "__main__":
    main()
