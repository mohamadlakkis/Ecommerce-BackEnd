def test_login_success(client):
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

    # Test login
    payload = {"username": "testuser", "password": "Testpass123"}
    response = client.post('/login', json=payload)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Login successful"

def test_login_invalid_credentials(client):
    payload = {"username": "nonexistent", "password": "wrongpass"}
    response = client.post('/login', json=payload)
    assert response.status_code == 401
    assert "Invalid username or password" in response.get_json()["error"]
