"""Run live end-to-end evaluations for Chicago Stroll."""

from uuid import uuid4

from app.graph import create_planner_graph
from evals.cases import EVAL_CASES
from evals.metrics import (
    has_itinerary,
    has_unknown_candidate_issue,
    itinerary_is_valid,
    repair_count,
    warning_count,
)


def run_case(graph,case: dict,) -> dict:
    """Run one evaluation case through the real planner."""

    thread_id = f"eval-{uuid4()}"
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    result = graph.invoke(
        {
            "user_message": case["message"],
        },
        config=config,
    )

    if result.get("clarification_question"):
        raise RuntimeError(
            (
                "Evaluation case did not provide enough "
                "information to reach planning. "
                f"Missing fields: "
                f"{result.get('missing_fields', [])}. "
                f"Question: "
                f"{result.get('clarification_question')}"
            )
        )

    if result.get("critique_result") is None:
        raise RuntimeError(
            "Evaluation case completed without a critique result."
        )

    return result


def main() -> None:
    """Run the live evaluation suite and print summary metrics."""

    graph = create_planner_graph()

    results: list[dict] = []

    print(
        f"\nRunning {len(EVAL_CASES)} "
        "Chicago Stroll evaluation cases...\n"
    )

    for index, case in enumerate(
        EVAL_CASES,
        start=1,
    ):
        print(
            f"[{index}/{len(EVAL_CASES)}] "
            f"{case['name']}"
        )

        try:
            result = run_case(
                graph,
                case,
            )

            results.append(
                result
            )

            print(
                "  itinerary generated:",
                has_itinerary(result),
            )

            print(
                "  valid:",
                itinerary_is_valid(
                    result
                ),
            )

            print(
                "  repairs:",
                repair_count(
                    result
                ),
            )

            print(
                "  warnings:",
                warning_count(
                    result
                ),
            )

            print(
                "  unknown candidate:",
                has_unknown_candidate_issue(
                    result
                ),
            )

        except Exception as error:
            print(
                f"  ERROR: {error}"
            )

            results.append(
                {
                    "evaluation_error": str(
                        error
                    )
                }
            )

        print()

    successful_results = [
        result
        for result in results
        if "evaluation_error"
        not in result
    ]

    total = len(
        results
    )

    successful = len(
        successful_results
    )

    if successful == 0:
        print(
            "No evaluation cases completed successfully."
        )
        return

    itinerary_count = sum(has_itinerary(result)for result in successful_results)

    valid_count = sum(itinerary_is_valid(result)for result in successful_results)

    unknown_count = sum(has_unknown_candidate_issue(result)for result in successful_results)

    average_repairs = (
        sum(
            repair_count(result)
            for result in successful_results
        )
        / successful
    )

    average_warnings = (
        sum(
            warning_count(result)
            for result in successful_results
        )
        / successful
    )

    print(
        "===== EVALUATION SUMMARY ====="
    )

    print(
        f"Cases: {total}"
    )

    print(
        f"Completed successfully: "
        f"{successful}/{total}"
    )

    print(
        "Planning completion rate: "
        f"{itinerary_count / successful:.1%}"
    )

    print(
        "Valid itinerary rate: "
        f"{valid_count / successful:.1%}"
    )

    print(
        "Unknown candidate rate: "
        f"{unknown_count / successful:.1%}"
    )

    print(
        "Average repairs: "
        f"{average_repairs:.2f}"
    )

    print(
        "Average warnings: "
        f"{average_warnings:.2f}"
    )


    

if __name__ == "__main__":
    main()