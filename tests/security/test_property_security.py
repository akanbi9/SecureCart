import pytest

from app.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def login(client, username, password):
    return client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": password
        }
    )


def test_customer_cannot_change_role_to_admin(client):
    login(client, "customer1", "Customer123!")

    response = client.patch(
        "/api/v1/me",
        json={
            "full_name": "Customer One",
            "role": "admin"
        }
    )

    assert response.status_code == 200

    profile_response = client.get("/api/v1/me")
    profile = profile_response.get_json()

    assert profile["role"] == "customer"
    assert profile["full_name"] == "Customer One"


def test_customer_cannot_change_role_using_profile_update(client):
    login(client, "customer2", "Customer123!")

    client.patch(
        "/api/v1/me",
        json={
            "role": "support"
        }
    )

    profile_response = client.get("/api/v1/me")
    profile = profile_response.get_json()

    assert profile["role"] == "customer"
    