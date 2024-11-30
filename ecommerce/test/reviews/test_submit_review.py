def test_submit_review_success(client, setup_reviews):
    payload = {
        "username": "admin",
        "password": "AdminPass123",
        "product_id": 1,
        "rating": 5,
        "comment": "Great product!"
    }
    response = client.post('/reviews/submit', json=payload)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Review submitted successfully"

def test_submit_review_unauthorized(client, setup_reviews):
    payload = {
        "username": "regular",
        "password": "UserPass123",
        "product_id": 1,
        "rating": 4,
        "comment": "Nice product"
    }
    response = client.post('/reviews/submit', json=payload)
    assert response.status_code == 403
    assert response.get_json()["error"] == "Unauthorized. Only employees can submit reviews."

def test_submit_review_missing_fields(client, setup_reviews):
    payload = {
        "username": "admin",
        "password": "AdminPass123",
        "product_id": 1
    }  # Missing 'rating' and 'comment'
    response = client.post('/reviews/submit', json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing fields"

def test_submit_review_invalid_rating(client, setup_reviews):
    payload = {
        "username": "admin",
        "password": "AdminPass123",
        "product_id": 1,
        "rating": 6,  # Invalid rating
        "comment": "Bad rating test"
    }
    response = client.post('/reviews/submit', json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Rating must be between 1 and 5"
