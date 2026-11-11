
def test_customer_login_success(client):
    # Register a new customer.
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "login_customer",
            "password": "SecurePass123!"
        }
    )

    assert register_response.status_code == 201

    # Log in with the registered account.
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "login_customer",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data is not None
    assert data["role"] == "customer"
