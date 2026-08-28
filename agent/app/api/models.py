from pydantic import BaseModel,Field
class PlanRequest(BaseModel): message:str
class ContinueRequest(BaseModel): thread_id:str; message:str
class PlanResponse(BaseModel):
    thread_id:str
    clarification_question:str|None=None
    itinerary:dict|None=None
    ready_for_research:bool|None=None
    warnings:list[str]=Field(default_factory=list)
    final_status:str|None=None
    agent_metrics:dict=Field(default_factory=dict)
