
def login(client, username, password):
    return client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": password
        }
    )


def test_customer_cannot_access_admin_dashboard(client):
    login(client, "customer1", "Customer123!")

    response = client.get("/admin/dashboard")

    assert response.status_code == 403


def test_customer_cannot_view_all_admin_orders(client):
    login(client, "customer1", "Customer123!")

    response = client.get("/api/v1/admin/orders")

    assert response.status_code == 403
    assert response.get_json()["error"] == "Admin access required"


def test_customer_cannot_access_support_dashboard(client):
    login(client, "customer1", "Customer123!")

    response = client.get("/support/dashboard")

    assert response.status_code == 403
    assert response.get_json()["error"] == "Support access required"


def test_admin_cannot_access_support_orders(client):
    login(client, "admin1", "Admin123!")

    response = client.get("/api/v1/support/orders")

    assert response.status_code == 403
    assert response.get_json()["error"] == "Support access required"


def test_admin_cannot_assign_order_without_csrf(client):
    response = login(client, "admin1", "Admin123!")
    assert response.status_code == 200

    response = client.patch(
        "/api/v1/admin/orders/5/assignment",
        json={"support_id": 3}
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == (
        "Invalid or missing CSRF token"
    )


def test_support_sees_only_assigned_orders(client):
    response = login(client, "support1", "Support123!")
    assert response.status_code == 200

    response = client.get("/api/v1/support/orders")

    assert response.status_code == 200

    orders = response.get_json()["orders"]

    # All returned orders must belong to support1.
    # The test database identifies support1 as user ID 3.
    for order in orders:
        assert order["id"] != 3

def test_support_sees_only_assigned_orders(client):
    from app.database import get_db

    db = get_db()

    support = db.execute(
        "SELECT id FROM users WHERE username = ?",
        ("support1",)
    ).fetchone()

    assert support is not None

    # Assign only Order #1 to support1.
    db.execute(
        """
        UPDATE orders
        SET assigned_support_id = ?
        WHERE id = ?
        """,
        (support["id"], 1)
    )

    db.commit()
    db.close()

    # Log in as support1.
    response = login(client, "support1", "Support123!")
    assert response.status_code == 200

    # Request assigned orders.
    response = client.get("/api/v1/support/orders")

    assert response.status_code == 200

    orders = response.get_json()["orders"]

    # Only Order #1 should be visible.
    order_ids = [order["id"] for order in orders]

    assert order_ids == [1]


def test_support_cannot_view_unassigned_order(client):
    from app.database import get_db

    db = get_db()

    support = db.execute(
        "SELECT id FROM users WHERE username = ?",
        ("support1",)
    ).fetchone()

    assert support is not None

    # Assign Order #1 to support1.
    db.execute(
        """
        UPDATE orders
        SET assigned_support_id = ?
        WHERE id = ?
        """,
        (support["id"], 1)
    )

    db.commit()
    db.close()

    # Log in as support1.
    response = login(client, "support1", "Support123!")
    assert response.status_code == 200

    # Support1 can access their assigned order.
    response = client.get("/api/v1/support/orders/1")
    assert response.status_code == 200

    # Support1 cannot access unassigned Order #3.
    response = client.get("/api/v1/support/orders/3")

    assert response.status_code == 403
    assert response.get_json()["error"] == "Access denied"
