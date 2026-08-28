# Chicago Stroll Agent

A bounded, tool-calling itinerary agent built with LangGraph. The model
chooses when to search live places, inspect place data, check travel
information, or submit an itinerary. A deterministic critic validates
the result, while a model-directed recovery policy handles failed plans.

Parse / Update Request
        ↓
   Planning Agent
    ↙        ↘
Tool Calls   DraftItinerary
    ↑             ↓
    └───────   Critic
                  ↓
              Recovery
           ↙    ↓    ↘
        repair replan clarify

## Tools

- `SearchPlaces` — discover places by category and area
- `FindPlace` — find a specific named place or landmark
- `GetPlaceDetails` — retrieve additional information about a candidate
- `GetTravelTime` — estimate travel time between locations
- `CheckHours` — retrieve available opening-hours evidence
- `DraftItinerary` — submit a structured itinerary for validation

- Maximum planner steps: 8
- Maximum tool calls: 12
- Maximum repairs: 2
- Maximum replans: 2

When the critic rejects an itinerary, the recovery agent chooses the
next action based on the validation result:

- `repair` — locally repair the current itinerary
- `replan` — construct a new plan using existing evidence
- `search_again` — return to planning and gather additional evidence
- `ask_user` — request clarification when the constraints cannot be resolved
- `best_effort` — return the best available result when further recovery
  is not appropriate
  