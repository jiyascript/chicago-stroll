"""LangGraph node marking the request ready for research"""
from app.state import PlannerState

def ready_for_research(state: PlannerState) -> dict:
    return {
        "ready_for_research": True,
        "clarification_question": None,
    }