from pathlib import Path
import sys

# Allow this script to import from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database import DATABASE, init_db
from app.seed import seed_users
from app.seed_products import seed_products
from app.seed_orders import seed_orders


def reset_database():
    if DATABASE.exists():
        DATABASE.unlink()
        print("Old database removed.")

    init_db()
    print("Fresh SecureCart database created.")

    seed_users()
    print("Default users created.")

    seed_products()
    print("Default products created.")

    seed_orders()
    print("Sample orders created.")


if __name__ == "__main__":
    reset_database()