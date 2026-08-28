from app.graph.router import route_planner_agent, route_after_tools

class _Msg:
    def __init__(self, tool_calls): self.tool_calls = tool_calls

def test_route_agent_to_tools_when_tool_calls_present():
    s = {"messages": [_Msg([{"name": "SearchPlaces", "args": {}, "id": "1"}])], "planner_steps": 1}
    assert route_planner_agent(s) == "planner_tools"

def test_route_agent_force_submits_when_budget_exhausted():
    s = {"messages": [_Msg([])], "planner_steps": 6}
    assert route_planner_agent(s) == "force_submit"

def test_route_after_tools_goes_to_critic_once_draft_exists():
    assert route_after_tools({"draft_itinerary": {"stops": []}}) == "critic"
    assert route_after_tools({}) == "planner_agent"