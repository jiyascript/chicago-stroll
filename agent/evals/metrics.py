def itinerary_is_valid(result: dict) -> bool:
    critique = result.get("critique_result") or {}
    return bool(critique.get("is_valid"))


def repair_count(result: dict) -> int:
    return int(result.get("repair_count", 0))


def has_unknown_candidate_issue(result: dict) -> bool:
    critique = result.get("critique_result") or {}

    issues = critique.get("issues", [])

    return any(
        "unknown candidate_id" in issue.lower()
        for issue in issues
    )


def warning_count(result: dict) -> int:
    critique = result.get("critique_result") or {}
    return len(critique.get("warnings", []))

def has_itinerary(result: dict)->bool:
    itinerary=result.get("draft_itinerary")
    return bool(itinerary and itinerary.get("stops"))
