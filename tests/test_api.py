from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_strategies():
    response = client.get("/api/strategies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 8


def test_get_customers():
    response = client.get("/api/customers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_get_customers_with_difficulty():
    response = client.get("/api/customers?difficulty=2")
    assert response.status_code == 200
    data = response.json()
    for persona in data:
        assert len(persona["evolved_objections"]) >= 2


def test_get_rules_empty():
    response = client.get("/api/rules")
    assert response.status_code == 200


def test_get_memory():
    response = client.get("/api/memory")
    assert response.status_code == 200
    data = response.json()
    assert "total_rules" in data
