def test_charge_wallet_success(client):
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

    # Charge wallet
    payload = {"amount": 50}
    response = client.put('/customers/testuser/charge', json=payload)
    assert response.status_code == 200
    assert "Wallet charged successfully" in response.get_json()["message"]

def test_deduct_wallet_insufficient_funds(client):
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

    # Explicitly set the wallet balance to 0
    client.put('/customers/testuser/charge', json={"amount": 0})

    # Check initial wallet balance
    wallet_balance = client.get('/customers/testuser').get_json().get('wallet_balance')
    print(f"Initial wallet balance: {wallet_balance}")  # Debugging output

    # Attempt to deduct from an empty wallet
    payload = {"amount": 50}
    response = client.put('/customers/testuser/deduct', json=payload)
    print("Response data:", response.get_json())  # Debugging output
    assert response.status_code == 400
