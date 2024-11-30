def test_add_goods_success(client):
    payload = {
        "name": "New Item",
        "category": "Test Category",
        "price": 15.99,
        "description": "A test item",
        "count": 30
    }
    response = client.post('/inventory/add', json=payload)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Item added successfully"

def test_add_goods_missing_fields(client):
    payload = {
        "name": "New Item",
        "category": "Test Category"
    }
    response = client.post('/inventory/add', json=payload)
    assert response.status_code == 400
    assert "Missing required fields" in response.get_json()["error"]
