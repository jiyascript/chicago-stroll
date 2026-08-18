from pydantic import BaseModel
class PlanRequest(BaseModel):
    message: str

class ContinueRequest(BaseModel):
    thread_id: str
    message: str

class PlanResponse(BaseModel):
    thread_id: str
    clarification_question: str | None = None
    itinerary: dict | None = None
    ready_for_research: bool | None = None