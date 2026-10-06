from werkzeug.security import generate_password_hash

from database import get_db, init_db


def create_user(username, password, role):
    db = get_db()

    password_hash = generate_password_hash(password)

    db.execute(
        """
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
        """,
        (username, password_hash, role)
    )

    db.commit()
    db.close()


def seed_users():
    users = [
        ("customer1", "Customer123!", "customer"),
        ("customer2", "Customer123!", "customer"),
        ("support1", "Support123!", "support"),
        ("admin1", "Admin123!", "admin"),
    ]

    for username, password, role in users:
        try:
            create_user(username, password, role)
            print(f"Created: {username} ({role})")
        except Exception as error:
            print(f"Could not create {username}: {error}")


if __name__ == "__main__":
    init_db()
    seed_users()
    print("User seeding complete.")