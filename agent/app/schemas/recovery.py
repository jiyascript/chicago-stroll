from typing import Literal
from pydantic import BaseModel
RecoveryAction = Literal["finish","repair","replan","search_again","ask_user","best_effort"]
class RecoveryDecision(BaseModel):
    action: RecoveryAction
    reason: str
