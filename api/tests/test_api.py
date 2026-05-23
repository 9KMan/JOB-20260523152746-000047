import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_trigger_pipeline():
    response = client.post(
        "/api/v1/pipeline/trigger",
        json={"dag_id": "ingestion_dag"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "triggered"

def test_list_sources():
    response = client.get("/api/v1/sources")
    assert response.status_code == 200
    assert "sources" in response.json()

def test_register_source():
    response = client.post(
        "/api/v1/sources",
        json={
            "source_id": "test_source",
            "source_type": "rest_api",
            "config": {"base_url": "https://example.com"}
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "registered"

def test_get_metrics():
    response = client.get("/api/v1/metrics/summary")
    assert response.status_code == 200
    assert "timestamp" in response.json()