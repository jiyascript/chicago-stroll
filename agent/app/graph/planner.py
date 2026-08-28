"""Main LangGraph workflow for Chicago Stroll."""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from app.graph.router import (
    route_after_completeness,
    route_after_critic,
    route_after_tools,
    route_initial_request,
    route_planner_agent,
    route_after_recovery,
    route_after_force_submit
)
from app.nodes import (
    check_completeness,
    create_clarification,
    critic_node,
    force_submit,
    parse_request,
    planner_agent,
    planner_tools,
    ready_for_research,
    repair_node,
    update_request,
    recovery_agent,
    prepare_replan,
    ask_user_from_recovery,
    mark_best_effort
)
from app.state import PlannerState


def create_planner_graph():
    """Create and compile the planner workflow."""

    builder = StateGraph(PlannerState)

    # --- nodes ---
    builder.add_node("parse_request", parse_request)
    builder.add_node("update_request", update_request)
    builder.add_node("check_completeness", check_completeness)
    builder.add_node("create_clarification", create_clarification)
    builder.add_node("ready_for_research", ready_for_research)
    builder.add_node("planner_agent", planner_agent)
    builder.add_node("planner_tools", planner_tools)
    builder.add_node("force_submit", force_submit)
    builder.add_node("critic", critic_node)
    builder.add_node("repair", repair_node)
    builder.add_node("recovery", recovery_agent)
    builder.add_node("prepare_replan", prepare_replan)
    builder.add_node("ask_user", ask_user_from_recovery)
    builder.add_node("best_effort", mark_best_effort)

    # --- intake ---
    builder.add_conditional_edges(START, route_initial_request)
    builder.add_edge("parse_request", "check_completeness")
    builder.add_edge("update_request", "check_completeness")
    builder.add_conditional_edges("check_completeness", route_after_completeness)
    builder.add_edge("create_clarification", END)

    # --- agentic planning loop ---
    builder.add_edge("ready_for_research", "planner_agent")
    builder.add_conditional_edges(
        "planner_agent",
        route_planner_agent,
        {
            "planner_tools": "planner_tools",
            "force_submit": "force_submit",
            "planner_agent": "planner_agent",
        },
    )
    builder.add_conditional_edges(
        "planner_tools",
        route_after_tools,
        {
            "critic": "critic",
            "planner_agent": "planner_agent",
        },
    )
    builder.add_conditional_edges(
        "force_submit",
        route_after_force_submit,
        {
            "critic": "critic",
            "end": END,
        },
    )

    # --- critic / repair (unchanged) ---
    builder.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "finished": END,
            "recovery": "recovery",
        },
    )
    builder.add_conditional_edges(
        "recovery",
        route_after_recovery,
        {
            "repair": "repair",
            "replan": "prepare_replan",
            "ask_user": "ask_user",
            "best_effort": "best_effort",
        },
    )

    builder.add_edge("repair", "critic")
    builder.add_edge("prepare_replan", "planner_agent")
    builder.add_edge("ask_user", END)
    builder.add_edge("best_effort", END)
    builder.add_edge("repair", "critic")

    checkpointer = InMemorySaver()

    return builder.compile(checkpointer=checkpointer)