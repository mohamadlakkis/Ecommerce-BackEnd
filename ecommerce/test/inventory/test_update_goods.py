def test_update_goods_single_field(client, setup_inventory):
    payload = {"price": 25.99}
    response = client.patch('/inventory/1/update', json=payload)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Item updated successfully"

def test_update_goods_multiple_fields(client, setup_inventory):
    payload = {"price": 19.99, "count": 80}
    response = client.patch('/inventory/1/update', json=payload)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Item updated successfully"

def test_update_goods_item_not_found(client):
    payload = {"price": 25.99}
    response = client.patch('/inventory/99/update', json=payload)
    assert response.status_code == 404
    assert "Item not found" in response.get_json()["error"]

def test_update_goods_invalid_payload(client, setup_inventory):
    response = client.patch('/inventory/1/update', json={})
    assert response.status_code == 400
    assert "No data provided" in response.get_json()["error"]
