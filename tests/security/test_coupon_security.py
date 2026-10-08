


def login(client, username, password):
    return client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": password
        }
    )


def test_customer_cannot_apply_coupon_to_another_customers_order(client):
    login(client, "customer1", "Customer123!")

    # After reset, order 3 belongs to customer2.
    response = client.post(
        "/api/v1/orders/3/coupon",
        json={"coupon_code": "SECURE10"}
    )

    assert response.status_code == 403


def test_coupon_cannot_be_used_twice_by_same_customer(client):
    login(client, "customer1", "Customer123!")

    first_response = client.post(
        "/api/v1/orders/1/coupon",
        json={"coupon_code": "SECURE10"}
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/api/v1/orders/2/coupon",
        json={"coupon_code": "SECURE10"}
    )

    assert second_response.status_code == 409


def test_coupon_cannot_be_applied_to_paid_order(client):
    import os

    # Log in as the customer who owns order 1.
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "customer1",
            "password": "Customer123!"
        }
    )

    assert login_response.status_code == 200

    # Simulate successful payment for order 1.
    payment_response = client.post(
        "/api/v1/webhooks/mock-payment",
        json={
            "order_id": 1,
            "payment_status": "paid",
            "webhook_secret": os.environ["PAYMENT_WEBHOOK_SECRET"]
        }
    )

    assert payment_response.status_code == 200

    # Attempt to apply a coupon after payment.
    coupon_response = client.post(
        "/api/v1/orders/1/coupon",
        json={
            "coupon_code": "SECURE10"
        }
    )

    # A paid order should not accept further discounts.
    assert coupon_response.status_code == 409
