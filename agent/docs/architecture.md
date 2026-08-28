# Chicago Stroll v2 agent architecture

The system deliberately separates five concerns:

1. **LLM policy** — chooses the next planning or recovery action.
2. **Tools** — provide live external evidence through narrow schemas.
3. **Deterministic critic** — enforces invariants such as candidate grounding, time ordering, canonical visit duration, and travel feasibility.
4. **LangGraph** — persists state and executes the bounded loop.
5. **Budgets** — prevent runaway tool, repair, and replan cycles.

A place can only enter the final itinerary after being inserted into the candidate registry by `SearchPlaces`. This preserves grounding even though discovery is live.
