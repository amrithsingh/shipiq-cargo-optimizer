"""Integration tests using FastAPI's TestClient."""

# TestClient wraps the FastAPI app so we can make HTTP requests in tests
# without starting a real server.
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_INPUT = {
    "cargos": [
        {"id": "C1", "volume": 1234},
        {"id": "C2", "volume": 4352},
        {"id": "C3", "volume": 3321},
    ],
    "tanks": [
        {"id": "T1", "capacity": 3000},
        {"id": "T2", "capacity": 5000},
        {"id": "T3", "capacity": 2000},
    ],
}


def test_full_flow():
    """POST /input → POST /optimize → GET /results end-to-end."""
    # Step 1: submit input
    resp = client.post("/input", json=SAMPLE_INPUT)
    assert resp.status_code == 200
    assert resp.json()["cargos_received"] == 3

    # Step 2: run optimization
    resp = client.post("/optimize")
    assert resp.status_code == 200
    data = resp.json()
    assert "tank_allocations" in data
    assert "cargo_summaries" in data
    assert "summary" in data

    # Step 3: retrieve cached results
    resp = client.get("/results")
    assert resp.status_code == 200
    assert resp.json() == data  # same as optimize response


def test_optimize_without_input():
    """POST /optimize before any input → 400."""
    # Reset state by importing and clearing directly.
    from app import service
    service._state["input"] = None
    service._state["result"] = None

    resp = client.post("/optimize")
    assert resp.status_code == 400
    assert "No input data" in resp.json()["detail"]


def test_results_without_optimize():
    """GET /results before running optimize → 404."""
    from app import service
    service._state["input"] = None
    service._state["result"] = None

    resp = client.get("/results")
    assert resp.status_code == 404


def test_empty_cargo_list():
    """Submitting an empty cargo list should still work."""
    resp = client.post("/input", json={"cargos": [], "tanks": [{"id": "T1", "capacity": 500}]})
    assert resp.status_code == 200

    resp = client.post("/optimize")
    assert resp.status_code == 200
    assert resp.json()["summary"]["total_loaded_volume"] == 0


def test_health_check():
    """GET / returns healthy status."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
