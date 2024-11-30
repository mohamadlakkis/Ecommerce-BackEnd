import pytest
from app import application
import psycopg2

@pytest.fixture
def client():
    with application.test_client() as client:
        yield client

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
def setup_inventory(db_connection):
    """Fixture to populate the inventory table for testing."""
    cur = db_connection.cursor()
    cur.execute("DELETE FROM inventory")
    db_connection.commit()
    cur.execute("""
        INSERT INTO inventory (id, name, category, price, description, count)
        VALUES (1, 'Test Item 1', 'Category1', 10.99, 'Description 1', 100),
               (2, 'Test Item 2', 'Category2', 20.00, 'Description 2', 50)
    """)
    db_connection.commit()

    cur.execute("SELECT * FROM inventory")
    print("Inventory data after setup:", cur.fetchall()) 
    cur.close()
