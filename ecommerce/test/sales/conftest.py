import pytest
import psycopg2
from app import application
import bcrypt
# Database connection fixture
@pytest.fixture
def db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="customers_db",
        user="admin",
        password="adminpass",
        port=5432
    )
    yield conn
    conn.close()

@pytest.fixture
def client():
    with application.test_client() as client:
        yield client

@pytest.fixture
def setup_sales(db_connection):
    cur = db_connection.cursor()
    try:
        cur.execute("DELETE FROM sales_history")
        cur.execute("DELETE FROM inventory")
        cur.execute("DELETE FROM customers")
        cur.execute(
            """
            INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet_balance, role)
            VALUES
            ('John Doe', 'johndoe', %s, 30, '123 Main St', 'Male', 'Single', 200.00, 'customer'),
            ('Jane Doe', 'janedoe', %s, 28, '456 Elm St', 'Female', 'Married', 50.00, 'customer')
            """,
            [bcrypt.hashpw('Password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
             bcrypt.hashpw('Password456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')]
        )
        cur.execute(
            """
            INSERT INTO inventory (id, name, category, price, description, count)
            VALUES
            (1, 'Item A', 'electronics', 20.00, 'Test Item A', 10),
            (2, 'Item B', 'clothing', 15.00, 'Test Item B', 5)
            """
        )
        cur.execute(
            """
            INSERT INTO sales_history (customer_id, good_id, quantity, total_price)
            VALUES
            (1, 1, 2, 40.00)
            """
        )
        db_connection.commit()
    finally:
        cur.close()
