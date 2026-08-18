from fastapi.testclient import TestClient
from app.api.server import app

client = TestClient(app)

def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }

def test_plan_endpoint_returns_threadid(monkeypatch)-> None:
    fake_result = {
        "clarification_question": (
            "What date are you planning for?"
        ),
        "ready_for_research": False,
        "draft_itinerary": None,
        "retrieved_places": [],
    }

    def fake_invoke(
        input_data,
        config,
    ):
        return fake_result

    monkeypatch.setattr(
        "app.api.routes.graph.invoke",
        fake_invoke,
    )

    response = client.post(
        "/plan",
        json={
            "message": (
                "Plan an architecture day "
                "in Chicago."
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["thread_id"]
    assert (
        data["clarification_question"]
        == "What date are you planning for?"
    )
    assert data["ready_for_research"] is False
    assert data["itinerary"] is None


def test_continue_endpoint_uses_existing_thread_id(monkeypatch,) -> None:
    """Continuation should preserve the supplied conversation ID."""

    fake_result = {
        "clarification_question": None,
        "ready_for_research": True,
        "draft_itinerary": None,
        "retrieved_places": [],
    }

    def fake_invoke(
        input_data,
        config,
    ):
        return fake_result

    monkeypatch.setattr(
        "app.api.routes.graph.invoke",
        fake_invoke,
    )

    thread_id = "test-thread-123"

    response = client.post(
        "/continue",
        json={
            "thread_id": thread_id,
            "message": "August 8, 2026",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["thread_id"] == thread_id
    assert data["clarification_question"] is None
    assert data["ready_for_research"] is True
