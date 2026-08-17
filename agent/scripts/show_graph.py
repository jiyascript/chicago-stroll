"""Render the Chicago Stroll LangGraph workflow"""
from app.graph import create_planner_graph
from pathlib import Path

def main() -> None:
    graph = create_planner_graph()
    mermaid = graph.get_graph().draw_mermaid()
    output = Path("docs")
    output.mkdir(exist_ok=True)
    graph_file = output / "planner_graph.md"
    graph_file.write_text(mermaid, encoding="utf-8",)
    print(f'saved to {graph_file}')

if __name__ == "__main__":
    main()