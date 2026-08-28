from langchain_core.messages import SystemMessage
from app.config.model import create_model,get_fallback_model_name
from app.prompts.recovery import RECOVERY_PROMPT
from app.schemas import RecoveryDecision
from app.services.model_invocation import invoke_runnable_with_fallback
from app.state import PlannerState

MAX_REPAIRS=2; MAX_REPLANS=2

def recovery_agent(state:PlannerState)->dict:
    critique=state["critique_result"]; prompt=f"""{RECOVERY_PROMPT}\nCritique: {critique}\nrepair_count={state.get('repair_count',0)}/{MAX_REPAIRS}\nreplan_count={state.get('replan_count',0)}/{MAX_REPLANS}"""
    p=create_model().with_structured_output(RecoveryDecision); f=create_model(get_fallback_model_name()).with_structured_output(RecoveryDecision)
    d=invoke_runnable_with_fallback(p,f,prompt)
    return {"recovery_decision":d.model_dump(mode="json")}

def prepare_replan(state:PlannerState)->dict:
    d=state["recovery_decision"]; action=d["action"]
    extra="Search live places again before submitting." if action=="search_again" else "Reconstruct the itinerary; existing candidates may be reused."
    return {"draft_itinerary":None,"critique_result":None,"recovery_feedback":d["reason"]+" "+extra,"replan_count":state.get("replan_count",0)+1,"planner_steps":0}

def ask_user_from_recovery(state:PlannerState)->dict:
    reason=(state.get("recovery_decision") or {}).get("reason","The current constraints cannot be satisfied safely.")
    return {"clarification_question":reason+" What constraint would you like to relax or clarify?","final_status":"needs_user_input"}

def mark_best_effort(state:PlannerState)->dict:
    critique=state.get("critique_result") or {}; warnings=list(critique.get("warnings",[])); warnings.extend(critique.get("issues",[])); critique={**critique,"warnings":warnings}
    return {"critique_result":critique,"final_status":"best_effort"}
