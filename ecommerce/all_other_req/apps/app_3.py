from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql
import os


app = Flask(__name__)

'''Database connection'''
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'), 
        database=os.getenv('DB_NAME', 'customers_db'),
        user=os.getenv('DB_USER', 'admin'),
        password=os.getenv('DB_PASSWORD', 'adminpass')
    )
    return conn

'''Service 4'''
import bcrypt

'''Verify username and password'''
def authenticate_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Fetch hashed password and role
        cur.execute("SELECT password, role FROM customers WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            return None, None  # User not found

        hashed_password, role = user

        # Validate password
        if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return None, None  # Invalid password

        return username, role
    finally:
        cur.close()
        conn.close()

@app.route('/reviews/submit', methods=['POST'])
def submit_review():
    """
    Submit a review for a product.

    Request JSON:
        {
            "username": "employee_username",
            "password": "employee_password",
            "product_id": 1,
            "rating": 5,
            "comment": "Great product!"
        }

    Returns:
        JSON:
            - 201 Created: {"message": "Review submitted successfully"}
            - 400 Bad Request: {"error": "Missing fields" or "Rating must be between 1 and 5"}
            - 401 Unauthorized: {"error": "Invalid username or password"}
            - 403 Forbidden: {"error": "Unauthorized. Only employees can submit reviews."}
            - 404 Not Found: {"error": "Customer not found"}
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    product_id = data.get('product_id')
    rating = data.get('rating')
    comment = data.get('comment')

    if not (username and password and product_id and rating):
        return jsonify({"error": "Missing fields"}), 400

    if not (1 <= rating <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    # Authenticate user
    _, role = authenticate_user(username, password)
    if not role:
        return jsonify({"error": "Invalid username or password"}), 401
    if role != 'emp':
        return jsonify({"error": "Unauthorized. Only employees can submit reviews."}), 403

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Fetch customer ID
        cur.execute("SELECT id FROM customers WHERE username = %s", (username,))
        customer = cur.fetchone()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        customer_id = customer[0]

        # Insert review
        cur.execute(
            """
            INSERT INTO reviews (customer_id, product_id, rating, comment)
            VALUES (%s, %s, %s, %s)
            """,
            (customer_id, product_id, rating, comment)
        )
        conn.commit()
        return jsonify({"message": "Review submitted successfully"}), 201

    finally:
        cur.close()
        conn.close()

@app.route('/reviews/<int:review_id>/update', methods=['PATCH'])
def update_review(review_id):
    """
    Update an existing review.

    Args:
        review_id (int): The ID of the review to update.

    Request JSON:
        {
            "username": "employee_username",
            "password": "employee_password",
            "rating": 4,
            "comment": "Updated comment"
        }

    Returns:
        JSON:
            - 200 OK: {"message": "Review updated successfully"}
            - 400 Bad Request: {"error": "Username and password are required" or "No fields to update"}
            - 401 Unauthorized: {"error": "Invalid username or password"}
            - 403 Forbidden: {"error": "Unauthorized. Only employees can update reviews."}
            - 404 Not Found: {"error": "Review not found"}
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    rating = data.get('rating')
    comment = data.get('comment')

    if not (username and password):
        return jsonify({"error": "Username and password are required"}), 400

    if not (rating or comment):
        return jsonify({"error": "No fields to update"}), 400

    if rating and not (1 <= rating <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    # Authenticate user
    _, role = authenticate_user(username, password)
    if not role:
        return jsonify({"error": "Invalid username or password"}), 401
    if role != 'emp':
        return jsonify({"error": "Unauthorized. Only employees can update reviews."}), 403

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Update review
        updates = []
        values = []
        if rating:
            updates.append("rating = %s")
            values.append(rating)
        if comment:
            updates.append("comment = %s")
            values.append(comment)

        values.append(review_id)

        cur.execute(
            f"UPDATE reviews SET {', '.join(updates)} WHERE id = %s",
            values
        )
        if cur.rowcount == 0:
            return jsonify({"error": "Review not found"}), 404
        conn.commit()
        return jsonify({"message": "Review updated successfully"}), 200

    finally:
        cur.close()
        conn.close()

@app.route('/reviews/<int:review_id>/delete', methods=['DELETE'])
def delete_review(review_id):
    """
    Delete a review by ID.

    Args:
        review_id (int): The ID of the review to delete.

    Request JSON:
        {
            "username": "employee_username",
            "password": "employee_password"
        }

    Returns:
        JSON:
            - 200 OK: {"message": "Review deleted successfully"}
            - 400 Bad Request: {"error": "Username and password are required"}
            - 401 Unauthorized: {"error": "Invalid username or password"}
            - 403 Forbidden: {"error": "Unauthorized. Only employees can delete reviews."}
            - 404 Not Found: {"error": "Review not found"}
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not (username and password):
        return jsonify({"error": "Username and password are required"}), 400

    _, role = authenticate_user(username, password)
    if not role:
        return jsonify({"error": "Invalid username or password"}), 401
    if role != 'emp':
        return jsonify({"error": "Unauthorized. Only employees can delete reviews."}), 403

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
        if cur.rowcount == 0:
            return jsonify({"error": "Review not found"}), 404
        conn.commit()
        return jsonify({"message": "Review deleted successfully"}), 200

    finally:
        cur.close()
        conn.close()
@app.route('/reviews/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """
    Get all reviews for a specific product.

    Args:
        product_id (int): The ID of the product.

    Returns:
        JSON:
            - 200 OK: List of reviews:
                [
                    {
                        "username": "customer_username",
                        "rating": 5,
                        "comment": "Excellent product!",
                        "review_date": "2024-11-29"
                    },
                    ...
                ]
            - 404 Not Found: {"error": "Product not found"}
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT customers.username, reviews.rating, reviews.comment, reviews.review_date
            FROM reviews
            JOIN customers ON reviews.customer_id = customers.id
            WHERE reviews.product_id = %s
            """,
            (product_id,)
        )
        reviews = cur.fetchall()

        result = [
            {
                "username": review[0],
                "rating": review[1],
                "comment": review[2],
                "review_date": review[3]
            }
            for review in reviews
        ]
        return jsonify(result), 200

    finally:
        cur.close()
        conn.close()
@app.route('/reviews/customer/<username>', methods=['GET'])
def get_customer_reviews(username):
    """
    Get all reviews submitted by a specific customer.

    Args:
        username (str): The username of the customer.

    Returns:
        JSON:
            - 200 OK: List of reviews:
                [
                    {
                        "product_name": "Product A",
                        "rating": 5,
                        "comment": "Loved it!",
                        "review_date": "2024-11-29"
                    },
                    ...
                ]
            - 404 Not Found: {"error": "Customer not found"}
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Fetch customer ID
        cur.execute("SELECT id FROM customers WHERE username = %s", (username,))
        customer = cur.fetchone()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        customer_id = customer[0]

        # Fetch reviews
        cur.execute(
            """
            SELECT inventory.name, reviews.rating, reviews.comment, reviews.review_date
            FROM reviews
            JOIN inventory ON reviews.product_id = inventory.id
            WHERE reviews.customer_id = %s
            """,
            (customer_id,)
        )
        reviews = cur.fetchall()

        result = [
            {
                "product_name": review[0],
                "rating": review[1],
                "comment": review[2],
                "review_date": review[3]
            }
            for review in reviews
        ]
        return jsonify(result), 200

    finally:
        cur.close()
        conn.close()
@app.route('/reviews/<int:review_id>/moderate', methods=['PATCH'])
def moderate_review(review_id):
    """
    Moderate a review by ID.

    Args:
        review_id (int): The ID of the review to moderate.

    Request JSON:
        {
            "username": "employee_username",
            "password": "employee_password",
            "status": "approved" or "flagged"
        }

    Returns:
        JSON:
            - 200 OK: {"message": "Review status updated to 'approved' or 'flagged'"}
            - 400 Bad Request: {"error": "Username, password, and status are required" or "Invalid status"}
            - 401 Unauthorized: {"error": "Invalid username or password"}
            - 403 Forbidden: {"error": "Unauthorized. Only employees can moderate reviews."}
            - 404 Not Found: {"error": "Review not found"}
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    status = data.get('status')
    if not (username and password and status):
        return jsonify({"error": "Username, password, and status are required"}), 400
    if status not in ['approved', 'flagged']:
        return jsonify({"error": "Invalid status. Allowed values are 'approved' or 'flagged'"}), 400

    _, role = authenticate_user(username, password)
    if not role:
        return jsonify({"error": "Invalid username or password"}), 401
    if role != 'emp':
        return jsonify({"error": "Unauthorized. Only employees can moderate reviews."}), 403

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "UPDATE reviews SET status = %s WHERE id = %s",
            (status, review_id)
        )
        if cur.rowcount == 0:
            return jsonify({"error": "Review not found"}), 404

        conn.commit()
        return jsonify({"message": f"Review status updated to '{status}'"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Failed to moderate review: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/reviews/<int:review_id>', methods=['GET'])
def get_review_details(review_id):
    """
    Get details of a specific review by ID.

    Args:
        review_id (int): The ID of the review.

    Returns:
        JSON:
            - 200 OK: Detailed review information:
                {
                    "username": "customer_username",
                    "product_name": "Product A",
                    "rating": 5,
                    "comment": "Amazing product!",
                    "status": "approved",
                    "review_date": "2024-11-29"
                }
            - 404 Not Found: {"error": "Review not found"}
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT customers.username, inventory.name, reviews.rating, reviews.comment, reviews.status, reviews.review_date
            FROM reviews
            JOIN customers ON reviews.customer_id = customers.id
            JOIN inventory ON reviews.product_id = inventory.id
            WHERE reviews.id = %s
            """,
            (review_id,)
        )
        review = cur.fetchone()
        if not review:
            return jsonify({"error": "Review not found"}), 404

        result = {
            "username": review[0],
            "product_name": review[1],
            "rating": review[2],
            "comment": review[3],
            "status": review[4],
            "review_date": review[5]
        }
        return jsonify(result), 200

    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
else:
    application = app