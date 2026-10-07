from app.database import get_db, init_db


def seed_orders():
    db = get_db()

    customer1 = db.execute(
        "SELECT id FROM users WHERE username = ?",
        ("customer1",)
    ).fetchone()

    customer2 = db.execute(
        "SELECT id FROM users WHERE username = ?",
        ("customer2",)
    ).fetchone()

    laptop = db.execute(
        "SELECT id, price FROM products WHERE name = ?",
        ("Laptop",)
    ).fetchone()

    mouse = db.execute(
        "SELECT id, price FROM products WHERE name = ?",
        ("Wireless Mouse",)
    ).fetchone()

    if not customer1 or not customer2 or not laptop or not mouse:
        db.close()
        raise RuntimeError(
            "Required users or products are missing. Seed users and products first."
        )

    sample_orders = [
        (customer1["id"], laptop["id"], 1, laptop["price"]),
        (customer1["id"], mouse["id"], 2, mouse["price"] * 2),
        (customer2["id"], mouse["id"], 1, mouse["price"]),
        (customer2["id"], laptop["id"], 1, laptop["price"]),
    ]

    for user_id, product_id, quantity, total in sample_orders:
        cursor = db.execute(
            """
            INSERT INTO orders (user_id, total, status)
            VALUES (?, ?, ?)
            """,
            (user_id, total, "pending")
        )

        order_id = cursor.lastrowid

        price = total / quantity

        db.execute(
            """
            INSERT INTO order_items
            (order_id, product_id, quantity, price_at_purchase)
            VALUES (?, ?, ?, ?)
            """,
            (order_id, product_id, quantity, price)
        )

    db.commit()
    db.close()

    print("4 sample orders created successfully.")


if __name__ == "__main__":
    init_db()
    seed_orders()


    