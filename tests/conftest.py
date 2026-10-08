import pytest

import app.database as database
from app.app import app
from app.seed import seed_users
from app.seed_products import seed_products
from app.seed_orders import seed_orders


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Use a fresh temporary database for each test.
    test_database = tmp_path / "securecart_test.db"
    monkeypatch.setattr(database, "DATABASE", test_database)

    # Create tables and sample records.
    database.init_db()
    seed_users()
    seed_products()
    seed_orders()

    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client