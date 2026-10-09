def login(client, username, password):
    return client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": password
        }
    )


def test_customer_cannot_access_admin_security_events(client):
    login(client, "customer1", "Customer123!")

    response = client.get("/api/v1/admin/security-events")

    assert response.status_code == 403
    assert response.get_json()["error"] == "Admin access required"


def test_customer_cannot_create_admin_product(client):
    login(client, "customer1", "Customer123!")

    response = client.post(
        "/api/v1/admin/products",
        json={
            "name": "Unauthorized Product",
            "description": "Should not be created",
            "price": 5000,
            "stock": 5
        }
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Admin access required"


def test_customer_cannot_view_another_customers_order(client):
    login(client, "customer1", "Customer123!")

    # After a fresh reset:
    # Orders 1 and 2 belong to customer1.
    # Orders 3 and 4 belong to customer2.
    response = client.get("/api/v1/orders/3")

    assert response.status_code == 403
    assert response.get_json()["error"] == "Access denied"