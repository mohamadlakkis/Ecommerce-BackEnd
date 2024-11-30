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

# Flask test client fixture
@pytest.fixture
def client():
    with application.test_client() as client:
        yield client

@pytest.fixture
def setup_reviews(db_connection):
    cur = db_connection.cursor()
    try:
        cur.execute("DELETE FROM reviews")
        cur.execute("DELETE FROM inventory")
        cur.execute("DELETE FROM customers")
        cur.execute(
            """
            INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, role)
            VALUES
            ('Admin User', 'admin', %s, 30, '123 Main St', 'Male', 'Single', 'emp'),
            ('Regular User', 'regular', %s, 25, '456 Elm St', 'Female', 'Married', 'customer')
            """,
            [bcrypt.hashpw('AdminPass123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
             bcrypt.hashpw('UserPass123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')]
        )
        cur.execute(
            """
            INSERT INTO inventory (id, name, category, price, description, count)
            VALUES
            (1, 'Product A', 'electronics', 99.99, 'A test product', 50)
            """
        )

        db_connection.commit()
    finally:
        cur.close()
