def test_deduct_goods_success(client, setup_inventory):
    payload = {"count": 10}
    response = client.put('/inventory/1/deduct', json=payload)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Stock deducted successfully"

def test_deduct_goods_insufficient_stock(client, setup_inventory):
    payload = {"count": 200}
    response = client.put('/inventory/1/deduct', json=payload)
    assert response.status_code == 400
    assert "Insufficient stock" in response.get_json()["error"]

def test_deduct_goods_invalid_count(client, setup_inventory):
    payload = {"count": -5}
    response = client.put('/inventory/1/deduct', json=payload)
    assert response.status_code == 400
    assert "Invalid count" in response.get_json()["error"]

def test_deduct_goods_item_not_found(client):
    payload = {"count": 10}
    response = client.put('/inventory/99/deduct', json=payload)
    assert response.status_code == 404
    assert "Item not found" in response.get_json()["error"]
