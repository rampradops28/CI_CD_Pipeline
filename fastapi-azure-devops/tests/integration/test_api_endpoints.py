import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestAPIEndpoints:
    """End-to-end integration tests for FastAPI HTTP routes."""

    def test_health_check(self, client: TestClient) -> None:
        """Test GET /health returns HTTP 200 and healthy payload."""
        response = client.get("/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "healthy"
        assert payload["service"] == "FastAPI CI Project"

    def test_create_and_get_user_flow(self, client: TestClient) -> None:
        """Test POST /users creates user, then GET /users/{id} retrieves it."""
        user_payload = {
            "email": "integration.user@example.com",
            "full_name": "Integration Tester",
        }
        create_res = client.post("/users", json=user_payload)
        assert create_res.status_code == 201
        created = create_res.json()
        assert created["id"] > 0
        assert created["email"] == user_payload["email"]
        assert created["full_name"] == user_payload["full_name"]
        assert created["is_active"] is True

        user_id = created["id"]
        get_res = client.get(f"/users/{user_id}")
        assert get_res.status_code == 200
        retrieved = get_res.json()
        assert retrieved["id"] == user_id
        assert retrieved["email"] == user_payload["email"]

    def test_create_duplicate_user_returns_400(self, client: TestClient) -> None:
        """Test POST /users returns 400 when email already exists."""
        user_payload = {
            "email": "duplicate.api@example.com",
            "full_name": "Original User",
        }
        res1 = client.post("/users", json=user_payload)
        assert res1.status_code == 201

        res2 = client.post("/users", json=user_payload)
        assert res2.status_code == 400
        assert "already registered" in res2.json()["detail"]

    def test_get_nonexistent_user_returns_404(self, client: TestClient) -> None:
        """Test GET /users/{id} returns 404 for missing ID."""
        res = client.get("/users/99999")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"]
