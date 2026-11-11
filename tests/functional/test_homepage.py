

def test_homepage_loads_successfully(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Welcome to SecureCart" in response.data
