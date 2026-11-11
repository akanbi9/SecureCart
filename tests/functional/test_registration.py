
from app.database import get_db
from werkzeug.security import check_password_hash


def test_customer_registration_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newcustomer",
            "password": "SecurePass123!"
        }
    )

    # Registration should succeed.
    assert response.status_code == 201
    assert response.get_json()["message"] == (
        "Registration successful"
    )

    # Verify the customer was saved.
    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE username = ?",
        ("newcustomer",)
    ).fetchone()

    db.close()

    assert user is not None
    assert user["role"] == "customer"

    # Verify the password is stored securely.
    assert user["password_hash"] != "SecurePass123!"

    assert check_password_hash(
        user["password_hash"],
        "SecurePass123!"
    )
