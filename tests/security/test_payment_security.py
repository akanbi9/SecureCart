from app.app import app


def test_payment_webhook_rejects_wrong_secret():
    with app.test_client() as client:
        response = client.post(
            "/api/v1/webhooks/mock-payment",
            json={
                "order_id": 1,
                "payment_status": "paid",
                "webhook_secret": "wrong-secret"
            }
        )

        assert response.status_code == 401
        assert response.get_json()["error"] == "Invalid payment notification"


def test_payment_webhook_rejects_invalid_status():
    with app.test_client() as client:
        response = client.post(
            "/api/v1/webhooks/mock-payment",
            json={
                "order_id": 1,
                "payment_status": "hacked",
                "webhook_secret": "securecart-local-payment-secret"
            }
        )

        assert response.status_code == 400
        assert response.get_json()["error"] == "Invalid payment status"


def test_payment_webhook_accepts_valid_notification():
    with app.test_client() as client:
        response = client.post(
            "/api/v1/webhooks/mock-payment",
            json={
                "order_id": 1,
                "payment_status": "paid",
                "webhook_secret": "securecart-local-payment-secret"
            }
        )

        assert response.status_code == 200
        assert response.get_json()["status"] == "paid"