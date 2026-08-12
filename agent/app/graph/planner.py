"""Main LangGraph workflow for Chicago Stroll"""
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from app.graph.router import (route_after_completeness, route_initial_request)
from app.nodes import (
    parse_request,
    check_completeness,
    create_clarification,
    ready_for_research,
    update_request,
    retrieve_places_node,
    planner_node
)
from app.state import PlannerState

def create_planner_graph():
    """Create and compile the planner workflow"""

    builder = StateGraph(PlannerState)
    builder.add_node("parse_request", parse_request)
    builder.add_node("update_request", update_request)
    builder.add_node("check_completeness", check_completeness)
    builder.add_node("create_clarification", create_clarification)
    builder.add_node("ready_for_research", ready_for_research)
    builder.add_node("retrieve_places", retrieve_places_node)
    builder.add_node("planner", planner_node)
    builder.add_conditional_edges(START,route_initial_request,)
    builder.add_edge("parse_request","check_completeness",)
    builder.add_edge("update_request","check_completeness",)
    builder.add_conditional_edges("check_completeness",route_after_completeness,)
    builder.add_edge("create_clarification", END,)
    builder.add_edge("ready_for_research","retrieve_places")
    builder.add_edge("retrieve_places", "planner",)
    builder.add_edge("planner", END)
    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer,)