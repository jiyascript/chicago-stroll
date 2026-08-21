from evals.metrics import (
    has_unknown_candidate_issue,
    itinerary_is_valid,
    repair_count,
    warning_count,
)


def test_itinerary_is_valid() -> None:
    result = {
        "critique_result": {
            "is_valid": True,
            "issues": [],
            "warnings": [],
        }
    }

    assert itinerary_is_valid(result) is True


def test_repair_count() -> None:
    result = {
        "repair_count": 2,
    }

    assert repair_count(result) == 2


def test_unknown_candidate_issue_detected() -> None:
    result = {
        "critique_result": {
            "is_valid": False,
            "issues": [
                "The itinerary references an unknown candidate_id: C99."
            ],
            "warnings": [],
        }
    }

    assert has_unknown_candidate_issue(result) is True


def test_warning_count() -> None:
    result = {
        "critique_result": {
            "warnings": [
                "Warning one.",
                "Warning two.",
            ]
        }
    }

    assert warning_count(result) == 2