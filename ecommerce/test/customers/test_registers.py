from memory_profiler import profile
import random
@profile
def test_register_customer_success(client):
    # Ensure the user does not already exist
    client.delete('/customers/testuser')  # Optional cleanup step

    payload = {
        "full_name": "Test User",
        "username": f"testuser{random.randint(1, 10000)}",
        "password": "Testpass123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single",
        "role": "customer"
    }
    response = client.post('/customers/register', json=payload)
    print("Response data:", response.get_json())  # Debugging output
    assert response.status_code == 201


def test_register_customer_missing_fields(client):
    payload = {
        "username": "testuser",
        "password": "Testpass123"
    }
    response = client.post('/customers/register', json=payload)
    assert response.status_code == 400
    assert "All fields are required" in response.get_json()["error"]

def test_register_customer_invalid_role(client):
    payload = {
        "full_name": "Test User",
        "username": "testuser",
        "password": "Testpass123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single",
        "role": "invalid_role"
    }
    response = client.post('/customers/register', json=payload)
    assert response.status_code == 400
    assert "Invalid role" in response.get_json()["error"]
