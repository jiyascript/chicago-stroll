def itinerary_is_valid(r): return bool((r.get("critique_result") or {}).get("is_valid"))
def has_itinerary(r): return bool((r.get("draft_itinerary") or {}).get("stops"))
def unknown_candidate_issue(r): return any("unknown candidate" in x.lower() for x in (r.get("critique_result") or {}).get("issues",[]))
def agent_metrics(r): return {"planner_steps":r.get("planner_steps",0),"tool_calls":r.get("tool_call_count",0),"repairs":r.get("repair_count",0),"replans":r.get("replan_count",0),"final_status":r.get("final_status")}
