from langchain_core.messages import HumanMessage,SystemMessage
from app.config.model import create_model,get_fallback_model_name
from app.prompts.intake import INTAKE_SYSTEM_PROMPT,UPDATE_SYSTEM_PROMPT
from app.schemas import TripRequest,TripRequestUpdate
from app.services.model_invocation import invoke_runnable_with_fallback
from app.state import PlannerState

REQUIRED_FIELDS=["date","start_time","end_time","start_location"]
def _structured(schema):
    p=create_model().with_structured_output(schema); f=create_model(get_fallback_model_name()).with_structured_output(schema); return p,f

def parse_request(state:PlannerState)->dict:
    p,f=_structured(TripRequest); req=invoke_runnable_with_fallback(p,f,[SystemMessage(INTAKE_SYSTEM_PROMPT),HumanMessage(state["user_message"])])
    return {"trip_request":req.model_dump(mode="json")}

def update_request(state:PlannerState)->dict:
    p,f=_structured(TripRequestUpdate); upd=invoke_runnable_with_fallback(p,f,[SystemMessage(UPDATE_SYSTEM_PROMPT),HumanMessage(state["user_message"])])
    current=TripRequest.model_validate(state["trip_request"]).model_dump(); delta=upd.model_dump(exclude_none=True)
    current.update(delta); return {"trip_request":TripRequest.model_validate(current).model_dump(mode="json"),"clarification_question":None}

def check_completeness(state:PlannerState)->dict:
    req=TripRequest.model_validate(state["trip_request"]); missing=[x for x in REQUIRED_FIELDS if getattr(req,x) in (None,"")]
    return {"missing_fields":missing,"ready_for_research":not missing}

def create_clarification(state:PlannerState)->dict:
    missing=state.get("missing_fields",[]); q="What " + " and ".join(x.replace("_"," ") for x in missing) + " should I use for your Chicago stroll?"
    return {"clarification_question":q,"ready_for_research":False,"final_status":"needs_user_input"}

def ready_for_research(state:PlannerState)->dict:
    return {"ready_for_research":True,"clarification_question":None,"draft_itinerary":None,"critique_result":None,"recovery_decision":None,"planner_steps":0,"tool_call_count":0,"final_status":"planning"}
