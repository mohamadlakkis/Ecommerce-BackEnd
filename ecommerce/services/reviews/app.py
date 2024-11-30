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
@app.route('/reviews/submit', methods=['POST'])
def submit_review():
    data = request.get_json()
    username = data.get('username')
    product_id = data.get('product_id')
    rating = data.get('rating')
    comment = data.get('comment')

    if not (username and product_id and rating):
        return jsonify({"error": "Missing fields"}), 400

    if not (1 <= rating <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

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
    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment')

    if not (rating or comment):
        return jsonify({"error": "No fields to update"}), 400

    if rating and not (1 <= rating <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

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
    data = request.get_json()
    status = data.get('status')

    if status not in ['approved', 'flagged']:
        return jsonify({"error": "Invalid status"}), 400

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
        return jsonify({"message": f"Review status updated to {status}"}), 200

    finally:
        cur.close()
        conn.close()
@app.route('/reviews/<int:review_id>', methods=['GET'])
def get_review_details(review_id):
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