import json

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from app.config.model import create_model, get_fallback_model_name
from app.prompts.planner import PLANNER_SYSTEM_PROMPT
from app.schemas import DraftItinerary, TripRequest
from app.services.agent_tools import (
    TOOLS,
    CheckHours,
    GetPlaceDetails,
    GetTravelTime,
    SearchPlaces,
    FindPlace,
    run_details,
    run_hours,
    run_search,
    run_travel,
    run_find
)
from app.services.geoapify_provider import GeoapifyProvider
from app.services.model_invocation import invoke_runnable_with_fallback
from app.state import PlannerState


MAX_PLANNER_STEPS = 8
MAX_TOOL_CALLS = 12


def _bound(name=None):
    return create_model(name).bind_tools(TOOLS)


def _initial_messages(req: TripRequest):
    return [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Trip request:\n"
                + req.model_dump_json(indent=2)
                + "\nPlan the itinerary using tools."
            )
        ),
    ]


def planner_agent(state: PlannerState) -> dict:
    req = TripRequest.model_validate(state["trip_request"])

    existing_messages = list(state.get("messages") or [])
    messages_to_persist = []

    # On the first planner call, create AND persist the initial conversation.
    if existing_messages:
        messages = list(existing_messages)
    else:
        initial = _initial_messages(req)
        messages = list(initial)
        messages_to_persist.extend(initial)

    # If the previous assistant response was prose instead of a tool call,
    # hand control back to Gemini with a user turn and persist that turn.
    if messages:
        last = messages[-1]

        if (
            getattr(last, "type", None) == "ai"
            and not getattr(last, "tool_calls", None)
        ):
            continuation = HumanMessage(
                content=(
                    "Continue planning. Do not respond with planning commentary. "
                    "Call the next appropriate tool, or call DraftItinerary if "
                    "you have enough grounded evidence to submit the itinerary."
                )
            )
            messages.append(continuation)
            messages_to_persist.append(continuation)

    # Recovery feedback is also a real user-side turn in the persisted
    # tool-calling conversation.
    feedback = state.get("recovery_feedback")
    if feedback:
        recovery_message = HumanMessage(
            content=(
                "The previous itinerary failed deterministic validation. "
                "Use this recovery feedback before continuing:\n"
                f"{feedback}"
            )
        )
        messages.append(recovery_message)
        messages_to_persist.append(recovery_message)

    ai = invoke_runnable_with_fallback(
        _bound(),
        _bound(get_fallback_model_name()),
        messages,
    )

    messages_to_persist.append(ai)

    return {
        "messages": messages_to_persist,
        "planner_steps": state.get("planner_steps", 0) + 1,
        "recovery_feedback": None,
    }


def planner_tools(state: PlannerState) -> dict:
    req = TripRequest.model_validate(state["trip_request"])
    provider = GeoapifyProvider()
    registry = list(state.get("retrieved_places", []))

    tool_msgs = []
    draft = None
    calls = 0

    for call in state["messages"][-1].tool_calls:
        calls += 1

        name = call["name"]
        call_id = call["id"]
        args = call.get("args", {})

        try:
            if name == "SearchPlaces":
                out, registry = run_search(
                    provider,
                    req,
                    SearchPlaces(**args),
                    registry,
                )
            elif name == "FindPlace":
                out, registry = run_find(
                    provider,
                    req,
                    FindPlace(**args),
                    registry,
                )
            elif name == "GetPlaceDetails":
                out = run_details(
                    provider,
                    registry,
                    GetPlaceDetails(**args),
                )

            elif name == "GetTravelTime":
                out = run_travel(
                    provider,
                    registry,
                    GetTravelTime(**args),
                )

            elif name == "CheckHours":
                out = run_hours(
                    provider,
                    registry,
                    CheckHours(**args),
                )

            elif name == "DraftItinerary":
                draft = DraftItinerary.model_validate(args)
                out = "Itinerary received for deterministic validation."

            else:
                out = f"Unknown tool {name}."

        except Exception as exc:
            out = json.dumps({"tool_error": str(exc)})

        # Every model tool call gets a corresponding ToolMessage.
        tool_msgs.append(
            ToolMessage(
                content=out,
                tool_call_id=call_id,
            )
        )

    update = {
        "messages": tool_msgs,
        "retrieved_places": registry,
        "tool_call_count": state.get("tool_call_count", 0) + calls,
    }

    if draft:
        update["draft_itinerary"] = draft.model_dump(mode="json")

    return update


def force_submit(state: PlannerState) -> dict:
    if not state.get("retrieved_places"):
        return {
            "final_status": "needs_user_input",
            "clarification_question": (
                "I could not gather enough live place evidence within the "
                "planning budget. Could you relax a location or activity "
                "constraint?"
            ),
        }

    model = create_model().bind_tools(
        [DraftItinerary],
        tool_choice="DraftItinerary",
    )

    # Treat this as a fresh forced-submission request rather than appending a
    # system message to an existing function-calling transcript.
    candidate_ids = [
        place.get("candidate_id")
        for place in state.get("retrieved_places", [])
        if place.get("candidate_id")
    ]

    req = TripRequest.model_validate(state["trip_request"])

    submit_messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "The planning budget is exhausted. Submit the safest grounded "
                "itinerary now using only discovered candidate IDs.\n\n"
                f"Trip request:\n{req.model_dump_json(indent=2)}\n\n"
                f"Allowed candidate IDs: {candidate_ids}"
            )
        ),
    ]

    ai = model.invoke(submit_messages)

    if not ai.tool_calls:
        raise RuntimeError(
            "Forced itinerary submission did not return a DraftItinerary tool call."
        )

    draft = DraftItinerary.model_validate(ai.tool_calls[0]["args"])

    return {
        "draft_itinerary": draft.model_dump(mode="json"),
    }