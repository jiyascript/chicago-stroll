from app.graph import create_planner_graph

def main():
    graph=create_planner_graph(); config={"configurable":{"thread_id":"demo"}}
    result=graph.invoke({"user_message":"Plan a Chicago architecture day from 11:00 to 18:00 starting in the Loop on September 12, 2026."},config=config)
    print(result)
if __name__=="__main__": main()
