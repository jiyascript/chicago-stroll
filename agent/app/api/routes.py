from uuid import uuid4
from fastapi import APIRouter 
from app.graph import create_planner_graph
from app.api.models import PlanRequest, PlanResponse, ContinueRequest
from app.schemas import DraftItinerary, RetrievedPlace
from app.services.itinerary_hydration import hydrate_itinerary

router = APIRouter()
graph = create_planner_graph()

def build_response(thread_id: str, result:dict,) -> PlanResponse:
    """Convert LangGraph state into an API response"""
    itinerary = None
    critique_result = result.get("critique_result") or {}
    draft_data = result.get("draft_itinerary")
    retrieved_data = result.get("retrieved_places", [],)
    if (draft_data is not None and retrieved_data):
        draft = DraftItinerary.model_validate(draft_data)
        candidates = [
            RetrievedPlace.model_validate(candidate)
            for candidate in retrieved_data
        ]
        resolved = hydrate_itinerary(itinerary=draft, candidates=candidates)
        itinerary = resolved.model_dump(mode="json")
    return PlanResponse(
        thread_id=thread_id,
        clarification_question=result.get(
            "clarification_question"
        ),
        itinerary=itinerary,
        ready_for_research=result.get(
            "ready_for_research"
        ),
        warnings=critique_result.get("warnings", []),
    )

@router.get("/health")
def health()->dict:
    return {
        "status": "ok"
    }

@router.post(
    "/plan",
    response_model=PlanResponse,
)
def plan_trip(request: PlanRequest,) -> PlanResponse:
    thread_id = str(uuid4())

    config = {
        "configurable": { "thread_id": thread_id,}
    }

    result = graph.invoke({"user_message": request.message,}, config=config)

    return build_response(thread_id=thread_id, result=result)
@router.post("/continue", response_model=PlanResponse)
def continue_trip(request: ContinueRequest,)-> PlanResponse:
    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }
    result = graph.invoke(
        {
            "user_message": request.message,
        },
        config=config
    )

    return build_response(
        thread_id=request.thread_id,
        result=result
    )
