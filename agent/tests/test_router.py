from types import SimpleNamespace
from app.graph.router import route_planner_agent,route_after_recovery

def test_tool_call_routes_to_tools():
    s={"messages":[SimpleNamespace(tool_calls=[{"name":"SearchPlaces"}])],"planner_steps":1,"tool_call_count":0}
    assert route_planner_agent(s)=="planner_tools"
def test_repair_budget_is_enforced():
    s={"recovery_decision":{"action":"repair"},"repair_count":2,"replan_count":0}
    assert route_after_recovery(s)=="best_effort"
def test_replan_budget_is_enforced():
    s={"recovery_decision":{"action":"search_again"},"repair_count":0,"replan_count":2}
    assert route_after_recovery(s)=="ask_user"
