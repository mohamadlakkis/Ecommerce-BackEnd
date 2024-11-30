from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql
import os
import re
import bcrypt

app = Flask(__name__)

def get_db_connection():
    """
    Establish a connection to the PostgreSQL database.

    Returns:
        psycopg2.connection: A connection object to the database.
    """
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'customers_db'),
        user=os.getenv('DB_USER', 'admin'),
        password=os.getenv('DB_PASSWORD', 'adminpass')
    )
    return conn

def is_valid_username(username):
    """
    Validate if a username is alphanumeric and between 3-50 characters.

    Args:
        username (str): The username to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.match("^[a-zA-Z0-9_]{3,50}$", username))

def is_valid_password(password):
    """
    Validate if a password is at least 8 characters long and contains both letters and numbers.

    Args:
        password (str): The password to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.match("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password))

def is_valid_age(age):
    """
    Validate if the age is a positive integer between 1 and 120.

    Args:
        age (int): The age to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return isinstance(age, int) and 1 <= age <= 120

def is_valid_role(role):
    """
    Validate if the role is either 'customer' or 'emp'.

    Args:
        role (str): The role to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return role in ['customer', 'emp']

@app.route('/customers/register', methods=['POST'])
def register_customer():
    """
    Register a new customer.

    Request JSON:
        {
            "full_name": "John Doe",
            "username": "johndoe",
            "password": "Password123",
            "age": 30,
            "address": "123 Main St",
            "gender": "Male",
            "marital_status": "Single",
            "role": "customer"
        }

    Returns:
        JSON:
            - 201 Created: {"message": "Customer registered successfully"}
            - 400 Bad Request: {"error": "Invalid input or username already exists"}
    """
    data = request.get_json()
    full_name = data.get('full_name')
    username = data.get('username')
    password = data.get('password')
    age = data.get('age')
    address = data.get('address')
    gender = data.get('gender')
    marital_status = data.get('marital_status')
    role = data.get('role', 'customer')

    # Validation checks
    if not (full_name and username and password and age and address and gender and marital_status):
        return jsonify({"error": "All fields are required"}), 400
    if not is_valid_username(username):
        return jsonify({"error": "Invalid username. Must be 3-50 alphanumeric characters."}), 400
    if not is_valid_password(password):
        return jsonify({"error": "Invalid password. Must be at least 8 characters with letters and numbers."}), 400
    if not is_valid_age(age):
        return jsonify({"error": "Invalid age. Must be a number between 1 and 120."}), 400
    if not is_valid_role(role):
        return jsonify({"error": "Invalid role. Allowed values are 'customer' or 'emp'."}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (full_name, username, hashed_password, age, address, gender, marital_status, role)
        )
        conn.commit()
        return jsonify({"message": "Customer registered successfully"}), 201

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"error": "Username already exists"}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    """
    Log in a customer.

    Request JSON:
        {
            "username": "johndoe",
            "password": "Password123"
        }

    Returns:
        JSON:
            - 200 OK: {"message": "Login successful", "user_id": 1, "role": "customer"}
            - 400 Bad Request: {"error": "Invalid username or password"}
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if not is_valid_username(username):
        return jsonify({"error": "Invalid username."}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, password, role FROM customers WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401

        user_id, hashed_password, role = user
        if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return jsonify({"error": "Invalid username or password"}), 401

        return jsonify({
            "message": "Login successful",
            "user_id": user_id,
            "role": role
        }), 200

    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()
@app.route('/customers/<username>', methods=['DELETE'])
def delete_customer(username):
    """
    Delete a customer from the database.

    Args:
        username (str): The username of the customer to delete.

    Returns:
        JSON:
            - 200 OK: {"message": "Customer deleted successfully"}
            - 404 Not Found: {"error": "Customer not found"}
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM customers WHERE username = %s", (username,))
    if cur.rowcount == 0:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": "Customer not found"}), 404

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Customer deleted successfully"}), 200


@app.route('/customers/<username>', methods=['PATCH'])
def update_customer(username):
    """
    Update a customer's information.

    Request JSON:
        {
            "key1": "value1",
            "key2": "value2",
            ...
        }

    Args:
        username (str): The username of the customer to update.

    Returns:
        JSON:
            - 200 OK: {"message": "Customer information updated successfully"}
            - 400 Bad Request: {"error": "No data provided"}
            - 404 Not Found: {"error": "Customer not found"}
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    updates = []
    values = []
    for key, value in data.items():
        updates.append(sql.Identifier(key) + sql.SQL(" = %s"))
        values.append(value)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            sql.SQL("UPDATE customers SET ") +
            sql.SQL(", ").join(updates) +
            sql.SQL(" WHERE username = %s"),
            values + [username]
        )
        if cur.rowcount == 0:
            return jsonify({"error": "Customer not found"}), 404
        conn.commit()
    finally:
        cur.close()
        conn.close()

    return jsonify({"message": "Customer information updated successfully"}), 200


@app.route('/customers', methods=['GET'])
def get_all_customers():
    """
    Retrieve a list of all customers.

    Returns:
        JSON:
            - 200 OK: [
                {
                    "id": 1,
                    "full_name": "John Doe",
                    "username": "johndoe",
                    "age": 30,
                    "address": "123 Main St",
                    "gender": "Male",
                    "marital_status": "Single",
                    "wallet_balance": 100.00
                },
                ...
            ]
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers")
    customers = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for customer in customers:
        result.append({
            "id": customer[0],
            "full_name": customer[1],
            "username": customer[2],
            "age": customer[4],
            "address": customer[5],
            "gender": customer[6],
            "marital_status": customer[7],
            "wallet_balance": customer[8]
        })
    return jsonify(result), 200


@app.route('/customers/<username>', methods=['GET'])
def get_customer(username):
    """
    Retrieve details of a specific customer.

    Args:
        username (str): The username of the customer to retrieve.

    Returns:
        JSON:
            - 200 OK: {
                "id": 1,
                "full_name": "John Doe",
                "username": "johndoe",
                "age": 30,
                "address": "123 Main St",
                "gender": "Male",
                "marital_status": "Single",
                "wallet_balance": 100.00
            }
            - 404 Not Found: {"error": "Customer not found"}
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE username = %s", (username,))
    customer = cur.fetchone()
    cur.close()
    conn.close()

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify({
        "id": customer[0],
        "full_name": customer[1],
        "username": customer[2],
        "age": customer[4],
        "address": customer[5],
        "gender": customer[6],
        "marital_status": customer[7],
        "wallet_balance": customer[8]
    }), 200


@app.route('/customers/<username>/charge', methods=['PUT'])
def charge_wallet(username):
    """
    Add money to a customer's wallet.

    Request JSON:
        {
            "amount": 50.00
        }

    Args:
        username (str): The username of the customer.

    Returns:
        JSON:
            - 200 OK: {"message": "Wallet charged successfully"}
            - 400 Bad Request: {"error": "Invalid amount"}
            - 404 Not Found: {"error": "Customer not found"}
    """
    data = request.get_json()
    amount = data.get('amount')
    if not amount or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE customers SET wallet_balance = wallet_balance + %s WHERE username = %s", (amount, username))
    if cur.rowcount == 0:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": "Customer not found"}), 404

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Wallet charged successfully"}), 200


@app.route('/customers/<username>/deduct', methods=['PUT'])
def deduct_wallet(username):
    """
    Deduct money from a customer's wallet.

    Request JSON:
        {
            "amount": 20.00
        }

    Args:
        username (str): The username of the customer.

    Returns:
        JSON:
            - 200 OK: {"message": "Wallet deduction successful"}
            - 400 Bad Request: {"error": "Invalid amount" or "Insufficient funds"}
            - 404 Not Found: {"error": "Customer not found"}
    """
    data = request.get_json()
    amount = data.get('amount')
    if not amount or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT wallet_balance FROM customers WHERE username = %s", (username,))
    customer = cur.fetchone()

    if not customer:
        cur.close()
        conn.close()
        return jsonify({"error": "Customer not found"}), 404

    if customer[0] < amount:
        cur.close()
        conn.close()
        return jsonify({"error": "Insufficient funds"}), 400

    cur.execute("UPDATE customers SET wallet_balance = wallet_balance - %s WHERE username = %s", (amount, username))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Wallet deduction successful"}), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
else:
    application = app