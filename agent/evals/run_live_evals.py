from uuid import uuid4
from app.graph import create_planner_graph
from evals.cases import EVAL_CASES
from evals.metrics import *
def main():
    g=create_planner_graph(); rows=[]
    for c in EVAL_CASES:
        r=g.invoke({"user_message":c["message"]},config={"configurable":{"thread_id":f"eval-{uuid4()}"}}); rows.append(r); print(c["name"],has_itinerary(r),itinerary_is_valid(r),agent_metrics(r))
    print("completion",sum(has_itinerary(r) for r in rows)/len(rows)); print("valid",sum(itinerary_is_valid(r) for r in rows)/len(rows)); print("unknown_candidate",sum(unknown_candidate_issue(r) for r in rows)/len(rows)); print("avg_tool_calls",sum(r.get("tool_call_count",0) for r in rows)/len(rows))
if __name__=="__main__": main()
