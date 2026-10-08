import pytest

from app.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_unauthenticated_user_cannot_view_profile(client):
    response = client.get("/api/v1/me")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


def test_login_rejects_wrong_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "customer1",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid username or password"


def test_login_accepts_correct_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "customer1",
            "password": "Customer123!"
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Login successful"
    assert data["username"] == "customer1"
    assert data["role"] == "customer"