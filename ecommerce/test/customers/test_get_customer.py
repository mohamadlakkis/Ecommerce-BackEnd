def test_get_customer_success(client):
    # Pre-register a user
    client.post('/customers/register', json={
        "full_name": "Test User",
        "username": "testuser",
        "password": "Testpass123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single",
        "role": "customer"
    })

    # Test fetching the user
    response = client.get('/customers/testuser')
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] == "testuser"
    assert data["age"] == 30

def test_get_customer_not_found(client):
    response = client.get('/customers/nonexistentuser')
    assert response.status_code == 404
    assert "Customer not found" in response.get_json()["error"]
