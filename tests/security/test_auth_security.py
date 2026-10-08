
def test_unauthenticated_user_cannot_view_profile(client):
    response = client.get("/api/v1/me")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


def test_login_rejects_wrong_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "customer1",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid username or password"


def test_login_accepts_correct_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "customer1",
            "password": "Customer123!"
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Login successful"
    assert data["username"] == "customer1"
    assert data["role"] == "customer"



def test_unauthenticated_user_cannot_view_profile(client):
    response = client.get("/api/v1/me")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


def test_login_rejects_wrong_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "customer1",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid username or password"


def test_login_accepts_correct_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "customer1",
            "password": "Customer123!"
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Login successful"
    assert data["username"] == "customer1"
    assert data["role"] == "customer"



def test_login_blocks_excessive_failed_attempts(client):
    # Attempt to log in with the wrong password repeatedly.
    responses = []

    for attempt in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "customer1",
                "password": "WrongPassword123!"
            }
        )

        responses.append(response.status_code)

    # The API should enforce a limit on repeated attempts.
    assert 429 in responses, (
        f"Expected HTTP 429 after excessive login attempts, "
        f"but received: {responses}"
    )
