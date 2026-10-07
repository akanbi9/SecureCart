from app.database import get_db, init_db


products = [
    ("Laptop", "Business laptop", 450000, 10),
    ("Wireless Mouse", "Wireless USB mouse", 15000, 25),
    ("Keyboard", "USB keyboard", 18000, 20),
    ("USB Flash Drive", "64GB USB flash drive", 12000, 30),
    ("Headphones", "Wireless headphones", 35000, 15),
    ("Webcam", "HD USB webcam", 28000, 12),
    ("Laptop Stand", "Adjustable laptop stand", 22000, 18),
    ("USB-C Hub", "Multi-port USB-C hub", 30000, 14),
    ("Phone Charger", "Fast USB-C charger", 16000, 20),
    ("Power Bank", "10000mAh power bank", 25000, 16),
]


def seed_products():
    db = get_db()

    for name, description, price, stock in products:
        existing_product = db.execute(
            "SELECT id FROM products WHERE name = ?",
            (name,)
        ).fetchone()

        if existing_product is None:
            db.execute(
                """
                INSERT INTO products (name, description, price, stock)
                VALUES (?, ?, ?, ?)
                """,
                (name, description, price, stock)
            )

    db.commit()
    db.close()

    print("Product seeding complete.")


if __name__ == "__main__":
    init_db()
    seed_products()