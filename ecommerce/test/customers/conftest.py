import pytest
from app import application
import pytest
import psycopg2

@pytest.fixture
def db_connection():
    # Create a direct connection to your production database
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
def client(db_connection):
    # Set up the Flask test client
    with application.test_client() as client:
        yield client