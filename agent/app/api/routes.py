from uuid import uuid4
from fastapi import APIRouter
from app.api.models import PlanRequest,ContinueRequest,PlanResponse
from app.graph import create_planner_graph
from app.schemas import DraftItinerary,RetrievedPlace
from app.services.itinerary_hydration import hydrate_itinerary
router=APIRouter(prefix="/api"); graph=create_planner_graph()

def build_response(thread_id:str,result:dict)->PlanResponse:
    itinerary=None; draft=result.get("draft_itinerary"); data=result.get("retrieved_places",[])
    if draft and data:
        itinerary=hydrate_itinerary(DraftItinerary.model_validate(draft),[RetrievedPlace.model_validate(x) for x in data]).model_dump(mode="json")
    critique=result.get("critique_result") or {}
    return PlanResponse(thread_id=thread_id,clarification_question=result.get("clarification_question"),itinerary=itinerary,ready_for_research=result.get("ready_for_research"),warnings=critique.get("warnings",[]),final_status=result.get("final_status") or ("complete" if critique.get("is_valid") else None),agent_metrics={"planner_steps":result.get("planner_steps",0),"tool_calls":result.get("tool_call_count",0),"repairs":result.get("repair_count",0),"replans":result.get("replan_count",0)})

@router.get("/health")
def health(): return {"status":"ok"}
@router.post("/plan",response_model=PlanResponse)
def plan_trip(request:PlanRequest):
    tid=str(uuid4()); result=graph.invoke({"user_message":request.message},config={"configurable":{"thread_id":tid}}); return build_response(tid,result)
@router.post("/continue",response_model=PlanResponse)
def continue_trip(request:ContinueRequest):
    result=graph.invoke({"user_message":request.message},config={"configurable":{"thread_id":request.thread_id}}); return build_response(request.thread_id,result)
