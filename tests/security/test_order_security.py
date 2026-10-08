
def login(client):
    return client.post(
        "/api/v1/auth/login",
        json={
            "username": "customer1",
            "password": "Customer123!"
        }
    )


def test_unauthenticated_user_cannot_create_order(client):
    response = client.post(
        "/api/v1/orders",
        json={"product_id": 1, "quantity": 1}
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


def test_order_rejects_missing_quantity(client):
    login(client)

    response = client.post(
        "/api/v1/orders",
        json={"product_id": 1}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Product ID and quantity are required"


def test_order_rejects_negative_quantity(client):
    login(client)

    response = client.post(
        "/api/v1/orders",
        json={"product_id": 1, "quantity": -5}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Quantity must be a positive integer"


def test_order_rejects_non_integer_quantity(client):
    login(client)

    response = client.post(
        "/api/v1/orders",
        json={"product_id": 1, "quantity": "five"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Quantity must be a positive integer"


def test_order_rejects_nonexistent_product(client):
    login(client)

    response = client.post(
        "/api/v1/orders",
        json={"product_id": 99999, "quantity": 1}
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Product not found"


def test_order_rejects_insufficient_stock(client):
    login(client)

    response = client.post(
        "/api/v1/orders",
        json={"product_id": 1, "quantity": 999999}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Not enough stock"


def test_order_ignores_customer_supplied_price(client):
    login(client)

    response = client.post(
        "/api/v1/orders",
        json={
            "product_id": 1,
            "quantity": 1,
            "total": 1
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    # The server must calculate the actual product price.
    assert data["total"] == 450000
    assert data["total"] != 1

def test_order_rejects_boolean_quantity(client):
    login(client)

    response = client.post(
        "/api/v1/orders",
        json={
            "product_id": 1,
            "quantity": True
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Quantity must be a positive integer"