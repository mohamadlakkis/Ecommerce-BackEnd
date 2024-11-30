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

'''Service 3'''
@app.route('/sales/display-goods', methods=['GET'])
def display_goods():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, price FROM inventory WHERE count > 0")
    goods = cur.fetchall()
    cur.close()
    conn.close()

    result = [{"name": good[0], "price": float(good[1])} for good in goods]
    return jsonify(result), 200
@app.route('/sales/goods/<int:good_id>', methods=['GET'])
def get_good_details(good_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventory WHERE id = %s", (good_id,))
    good = cur.fetchone()
    cur.close()
    conn.close()

    if not good:
        return jsonify({"error": "Good not found"}), 404

    result = {
        "id": good[0],
        "name": good[1],
        "category": good[2],
        "price": float(good[3]),
        "description": good[4],
        "count": good[5]
    }
    return jsonify(result), 200
@app.route('/sales/sell', methods=['POST'])
def process_sale():
    data = request.get_json()
    username = data.get('username')
    good_id = data.get('good_id')
    quantity = data.get('quantity')

    if not (username and good_id and quantity):
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Check if customer exists
        cur.execute("SELECT id, wallet_balance FROM customers WHERE username = %s", (username,))
        customer = cur.fetchone()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        customer_id, wallet_balance = customer

        # Check if good exists and has enough stock
        cur.execute("SELECT id, price, count FROM inventory WHERE id = %s", (good_id,))
        good = cur.fetchone()
        if not good:
            return jsonify({"error": "Good not found"}), 404

        _, price, stock = good

        if stock < quantity:
            return jsonify({"error": "Insufficient stock"}), 400

        # Check if customer has enough money
        total_price = price * quantity
        if wallet_balance < total_price:
            return jsonify({"error": "Insufficient funds"}), 400

        # Deduct money from customer's wallet and update inventory
        cur.execute("UPDATE customers SET wallet_balance = wallet_balance - %s WHERE id = %s", (total_price, customer_id))
        cur.execute("UPDATE inventory SET count = count - %s WHERE id = %s", (quantity, good_id))

        # Record the sale
        cur.execute(
            """
            INSERT INTO sales_history (customer_id, good_id, quantity, total_price)
            VALUES (%s, %s, %s, %s)
            """,
            (customer_id, good_id, quantity, total_price)
        )

        conn.commit()
        return jsonify({"message": "Purchase successful", "remaining_balance": wallet_balance - total_price}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()
@app.route('/sales/history/<username>', methods=['GET'])
def get_purchase_history(username):
    conn = get_db_connection()
    cur = conn.cursor()

    # Check if customer exists
    cur.execute("SELECT id FROM customers WHERE username = %s", (username,))
    customer = cur.fetchone()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    customer_id = customer[0]

    # Fetch purchase history
    cur.execute(
        """
        SELECT inventory.name, sales_history.quantity, sales_history.total_price, sales_history.sale_date
        FROM sales_history
        JOIN inventory ON sales_history.good_id = inventory.id
        WHERE sales_history.customer_id = %s
        """,
        (customer_id,)
    )
    history = cur.fetchall()
    cur.close()
    conn.close()

    result = [
        {
            "good_name": record[0],
            "quantity": record[1],
            "total_price": float(record[2]),
            "sale_date": record[3]
        }
        for record in history
    ]
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)