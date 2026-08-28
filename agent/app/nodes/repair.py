from app.config.model import create_model,get_fallback_model_name
from app.schemas import DraftItinerary
from app.services.model_invocation import invoke_runnable_with_fallback
from app.state import PlannerState

def repair_node(state:PlannerState)->dict:
    prompt=f"""Repair this itinerary using ONLY existing candidate IDs. Correct the deterministic critic issues without inventing places.\nItinerary: {state['draft_itinerary']}\nCandidates: {state.get('retrieved_places',[])}\nCritique: {state['critique_result']}"""
    p=create_model().with_structured_output(DraftItinerary); f=create_model(get_fallback_model_name()).with_structured_output(DraftItinerary)
    repaired=invoke_runnable_with_fallback(p,f,prompt)
    return {"draft_itinerary":repaired.model_dump(mode="json"),"repair_count":state.get("repair_count",0)+1}
