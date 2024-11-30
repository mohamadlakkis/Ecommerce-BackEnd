def test_display_goods(client, setup_sales):
    response = client.get('/sales/display-goods')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['name'] == 'Item A'
    assert data[1]['name'] == 'Item B'
def test_get_good_details(client, setup_sales):
    # Valid good
    response = client.get('/sales/goods/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Item A'
    assert data['price'] == 20.00

    # Invalid good
    response = client.get('/sales/goods/99')
    assert response.status_code == 404
    assert response.get_json()['error'] == 'Good not found'
def test_process_sale(client, setup_sales):
    # Successful sale
    response = client.post('/sales/sell', json={
        "username": "johndoe",
        "good_id": 1,
        "quantity": 1
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Purchase successful'

    # Insufficient stock
    response = client.post('/sales/sell', json={
        "username": "johndoe",
        "good_id": 2,
        "quantity": 10
    })
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Insufficient stock'

    # Insufficient funds
    response = client.post('/sales/sell', json={
        "username": "janedoe",
        "good_id": 1,
        "quantity": 5
    })
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Insufficient funds'

    # Non-existent customer
    response = client.post('/sales/sell', json={
        "username": "nonexistent",
        "good_id": 1,
        "quantity": 1
    })
    assert response.status_code == 404
    assert response.get_json()['error'] == 'Customer not found'

    # Non-existent good
    response = client.post('/sales/sell', json={
        "username": "johndoe",
        "good_id": 99,
        "quantity": 1
    })
    assert response.status_code == 404
    assert response.get_json()['error'] == 'Good not found'

def test_get_purchase_history(client, setup_sales):
    # Valid customer
    response = client.get('/sales/history/johndoe')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['good_name'] == 'Item A'

    # Non-existent customer
    response = client.get('/sales/history/nonexistent')
    assert response.status_code == 404
    assert response.get_json()['error'] == 'Customer not found'
