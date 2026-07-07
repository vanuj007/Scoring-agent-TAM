from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_score_endpoint():
    payload = {
        "company_type": "Startup",
        "employee_count": 200,
        "funding_status": "VC-backed",
        "revenue_band": "$1M-$100M",
        "geography": "US",
    }
    response = client.post("/score", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["tam_score"] == 20 + 25 + 20 + 15 + 18
    assert body["tam_decision"] == "Yes"


def test_score_endpoint_missing_required_field():
    payload = {
        "company_type": "Startup",
        "employee_count": 200,
        "funding_status": "VC-backed",
    }
    response = client.post("/score", json=payload)
    assert response.status_code == 422


def test_score_endpoint_invalid_enum():
    payload = {
        "company_type": "NotARealType",
        "employee_count": 200,
        "funding_status": "VC-backed",
        "geography": "US",
    }
    response = client.post("/score", json=payload)
    assert response.status_code == 422


def test_root_serves_form():
    response = client.get("/")
    assert response.status_code == 200
    assert "TAM Scoring Agent" in response.text
