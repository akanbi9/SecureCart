
from app.database import get_db


def test_customer_can_place_order(client):
    # Log in as an existing customer.
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "customer1",
            "password": "Customer123!"
        }
    )

    assert login_response.status_code == 200

    # Find the Laptop product and its price.
    db = get_db()

    product = db.execute(
        """
        SELECT id, price, stock
        FROM products
        WHERE name = ?
        """,
        ("Laptop",)
    ).fetchone()

    assert product is not None

    product_id = product["id"]
    price = product["price"]
    original_stock = product["stock"]

    db.close()

    # Place an order for one laptop.
    response = client.post(
        "/api/v1/orders",
        json={
            "product_id": product_id,
            "quantity": 1
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Order created successfully"
    assert data["quantity"] == 1
    assert data["total"] == price
    assert data["status"] == "pending"

    # Verify that the order was saved.
    db = get_db()

    order = db.execute(
        "SELECT * FROM orders WHERE id = ?",
        (data["order_id"],)
    ).fetchone()

    updated_product = db.execute(
        "SELECT stock FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    db.close()

    assert order is not None
    assert order["total"] == price
    assert order["status"] == "pending"

    # Confirm stock decreased by one.
    assert updated_product["stock"] == original_stock - 1

