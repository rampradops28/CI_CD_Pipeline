from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "Order Service"

def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_order():
    payload = {"item": "MacBook Pro", "quantity": 1}
    response = client.post("/orders", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 101
    assert data["status"] == "confirmed"
