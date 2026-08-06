"""Main LangGraph workflow for Chicago Stroll"""
from langgraph.graph import START, END, StateGraph
from app.nodes import (
    parse_request,
    check_completeness,
)
from app.state import PlannerState

def create_planner_graph():
    """Create and compile the planner workflow"""

    builder = StateGraph(PlannerState)
    builder.add_node("parse_request",parse_request)
    builder.add_node("check_completeness",check_completeness)
    builder.add_edge(START,"parse_request")
    builder.add_edge("parse_request","check_completeness")
    builder.add_edge("check_completeness",END)
    return builder.compile()