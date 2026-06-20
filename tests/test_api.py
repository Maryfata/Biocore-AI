"""API Tests"""
import pytest
from fastapi.testclient import TestClient
from api.main import app
from db.database import engine
from db.models import Base
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_and_get_patient(client):
    payload = {
        "medical_id": "PATIENT-001",
        "name": "Test User",
        "email": "test@example.com"
    }
    response = client.post("/api/patients", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "id" in body
    patient_id = body["id"]

    response = client.get(f"/api/patients/{patient_id}")
    assert response.status_code == 200
    assert response.json()["medical_id"] == "PATIENT-001"


def test_upload_signal(client):
    payload = {
        "signal_type": "ecg",
        "raw_signal": [0.0, 0.1, 0.2, 0.1, 0.0] * 30,
        "metadata": {"device": "simulated"}
    }
    patient_payload = {
        "medical_id": "PATIENT-002",
        "name": "Upload User",
        "email": "upload@example.com"
    }
    patient_resp = client.post("/api/patients", json=patient_payload)
    patient_id = patient_resp.json()["id"]
    response = client.post(f"/api/signals/upload/{patient_id}", json=payload)
    assert response.status_code == 200
    assert "signal_id" in response.json()
