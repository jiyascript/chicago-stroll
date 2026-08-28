from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from app.config.model import create_model, get_fallback_model_name
from app.prompts.planner_prompt import build_planner_prompt  # reuse trip formatting
from app.schemas import DraftItinerary, PlannerContext, RetrievedPlace, TripRequest
from app.services.model_invocation import invoke_runnable_with_fallback
from app.services.planner_tools import GetTravelTime, SearchPlaces, run_search, run_travel
from app.repositories import PlaceRepository
from app.state import PlannerState

MAX_PLANNER_STEPS = 6
TOOLS = [SearchPlaces, GetTravelTime, DraftItinerary]


def _bound(model_name=None):
    return create_model(model_name).bind_tools(TOOLS)


def planner_agent(state: PlannerState) -> dict:
    request = TripRequest.model_validate(state["trip_request"])
    messages = state.get("messages") or [
        SystemMessage(
            "You plan Chicago day itineraries. Use SearchPlaces (call it "
            "several times across neighborhoods/interests) to discover options, "
            "GetTravelTime to sanity-check spacing, then call DraftItinerary "
            "referencing only candidate_id values you discovered.\n\n"
            + build_planner_prompt(  # reuse your trip_lines block
                PlannerContext(trip_request=request, candidate_places=[])
            )
        ),
        HumanMessage("Plan the itinerary."),
    ]
    ai = invoke_runnable_with_fallback(
        _bound(), _bound(get_fallback_model_name()), messages
    )
    return {"messages": [ai], "planner_steps": state.get("planner_steps", 0) + 1}


def planner_tools(state: PlannerState) -> dict:
    request = TripRequest.model_validate(state["trip_request"])
    repo = PlaceRepository()
    registry = list(state.get("retrieved_places", []))
    tool_msgs, draft = [], None

    for call in state["messages"][-1].tool_calls:
        name, cid = call["name"], call["id"]
        if name == "SearchPlaces":
            out, registry = run_search(repo, request, SearchPlaces(**call["args"]), registry)
        elif name == "GetTravelTime":
            out = run_travel(registry, GetTravelTime(**call["args"]))
        elif name == "DraftItinerary":
            draft = DraftItinerary.model_validate(call["args"])
            out = "Itinerary received."
        else:
            out = f"Unknown tool {name}."
        tool_msgs.append(ToolMessage(content=out, tool_call_id=cid))

    update = {"messages": tool_msgs, "retrieved_places": registry}
    if draft is not None:
        update["draft_itinerary"] = draft.model_dump(mode="json")
    return update


def force_submit(state: PlannerState) -> dict:
    """Bound loop exceeded — force a DraftItinerary so we always terminate."""
    model = create_model().bind_tools([DraftItinerary], tool_choice="DraftItinerary")
    ai = model.invoke(state["messages"])
    draft = DraftItinerary.model_validate(ai.tool_calls[0]["args"])
    return {"draft_itinerary": draft.model_dump(mode="json")}