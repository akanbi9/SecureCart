

def test_products_are_available(client):
    response = client.get("/api/v1/products")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 10
