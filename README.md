# Chicago Stroll   ༘⋆༄.°⋆

**A bounded, tool-calling Chicago itinerary agent.** Chicago Stroll is an agentic day planner that uses model-directed tool calling, live place data, and constraint validation to build grounded Chicago itineraries.

**[Live app →](https://chicago-stroll.vercel.app/)**

![Chicago Stroll demo](docs/chi_stroll_demo.png)

## How It Works

Instead of following a fixed retrieval pipeline, the planning agent decides what information it needs and which tools to call as it builds an itinerary.

```text
User Request
     ↓
Request Intake
     ↓
Planning Agent ←→ Live Tools
     ↓
Draft Itinerary
     ↓
Deterministic Critic
     │
     ├── valid → Final Itinerary
     │
     └── invalid → Recovery Agent
                       ↓
              repair / replan /
              search / clarify
```

The agent can search for places, locate specific landmarks, inspect place details and hours, estimate travel time, and submit a structured itinerary.


## Key Features

- **Model-directed tool use** — Gemini chooses which tools to call and in what order based on the request and evidence gathered so far.
- **Live, grounded retrieval** — Geoapify provides real place data, registered as candidate IDs so the final itinerary stays grounded in retrieved results.
- **Validation & recovery** — a deterministic critic checks generated itineraries; failed plans can be repaired, replanned, or sent back for clarification.
- **Bounded execution** — explicit limits on planning steps, tool calls, repairs, and replans prevent uncontrolled agent loops.
- **Multi-turn planning** — missing or conflicting constraints can be clarified with the user while preserving conversation state.

## Tools

`SearchPlaces` · `FindPlace` · `GetPlaceDetails` · `GetTravelTime` · `CheckHours` · `DraftItinerary`

## Tech Stack

**Python · LangGraph · LangChain · Gemini · Geoapify · FastAPI · Pydantic · pytest · Vercel**

## Run Locally

```bash
cd agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your API keys to `.env`, then:

```bash
uvicorn api.index:app --reload
```

Run the tests with:

```bash
python -m pytest
```

## Documentation

See [`agent/README.md`](agent/README.md) and [`agent/docs/`](agent/docs/) for implementation and architecture details.