


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
