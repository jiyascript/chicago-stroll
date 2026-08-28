from typing import Literal
from app.state import PlannerState
from app.nodes.planning_agent import MAX_PLANNER_STEPS,MAX_TOOL_CALLS
from app.nodes.recovery import MAX_REPAIRS,MAX_REPLANS

def route_initial_request(state:PlannerState)->Literal["parse_request","update_request"]:
    return "parse_request" if state.get("trip_request") is None else "update_request"

def route_after_completeness(state:PlannerState)->Literal["create_clarification","ready_for_research"]:
    return "create_clarification" if state.get("missing_fields") else "ready_for_research"

def route_planner_agent(state:PlannerState)->Literal["planner_tools","force_submit","planner_agent"]:
    if state.get("planner_steps",0)>=MAX_PLANNER_STEPS or state.get("tool_call_count",0)>=MAX_TOOL_CALLS: return "force_submit"
    last=state["messages"][-1]
    return "planner_tools" if getattr(last,"tool_calls",None) else "planner_agent"
def route_after_force_submit(state: PlannerState,) -> Literal["critic", "end"]:
    if state.get("draft_itinerary"):
        return "critic"
    return "end"
def route_after_tools(state:PlannerState)->Literal["critic","planner_agent","ask_user"]:
    if state.get("draft_itinerary"): return "critic"
    if state.get("tool_call_count",0)>=MAX_TOOL_CALLS: return "planner_agent"
    return "planner_agent"

def route_after_critic(state:PlannerState)->Literal["finished","recovery"]:
    return "finished" if state["critique_result"]["is_valid"] else "recovery"

def route_after_recovery(state:PlannerState)->Literal["finished","repair","replan","ask_user","best_effort"]:
    action=state["recovery_decision"]["action"]
    if action=="finish": return "finished"
    if action=="repair": return "repair" if state.get("repair_count",0)<MAX_REPAIRS else "best_effort"
    if action in {"replan","search_again"}: return "replan" if state.get("replan_count",0)<MAX_REPLANS else "ask_user"
    if action=="ask_user": return "ask_user"
    return "best_effort"
