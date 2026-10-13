import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_health_endpoint(client: TestClient):
    """Test application health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


@pytest.mark.integration
def test_create_and_get_item(client: TestClient):
    """Integration test: Create an item via API, verify persisted record in database."""
    payload = {
        "name": "Production Database Server",
        "description": "PostgreSQL 15 High Availability Cluster",
    }
    create_res = client.post("/items/", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["id"] is not None
    assert created_data["name"] == payload["name"]
    assert created_data["description"] == payload["description"]

    # Verify retrieval by ID
    item_id = created_data["id"]
    get_res = client.get(f"/items/{item_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == payload["name"]


@pytest.mark.integration
def test_list_items(client: TestClient):
    """Integration test: List all created items from database."""
    client.post("/items/", json={"name": "Item A", "description": "First"})
    client.post("/items/", json={"name": "Item B", "description": "Second"})

    res = client.get("/items/")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 2


@pytest.mark.integration
def test_get_nonexistent_item_returns_404(client: TestClient):
    """Integration test: Retrieving invalid ID returns 404."""
    res = client.get("/items/999999")
    assert res.status_code == 404
    assert res.json()["detail"] == "Item not found"
