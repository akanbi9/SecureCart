

import os


def test_payment_webhook_rejects_wrong_secret(client):
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


def test_payment_webhook_rejects_invalid_status(client):
    response = client.post(
        "/api/v1/webhooks/mock-payment",
        json={
            "order_id": 1,
            "payment_status": "hacked",
            "webhook_secret": os.environ["PAYMENT_WEBHOOK_SECRET"]
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid payment status"


def test_payment_webhook_accepts_valid_notification(client):
    response = client.post(
        "/api/v1/webhooks/mock-payment",
        json={
            "order_id": 1,
            "payment_status": "paid",
            "webhook_secret": os.environ["PAYMENT_WEBHOOK_SECRET"]
        }
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "paid"


def test_payment_webhook_rejects_old_hardcoded_secret(client):
    response = client.post(
        "/api/v1/webhooks/mock-payment",
        json={
            "order_id": 1,
            "payment_status": "paid",
            "webhook_secret": "securecart-local-payment-secret"
        }
    )

    assert response.status_code == 401
