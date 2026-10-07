from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db, init_db

app = Flask(__name__)

app.secret_key = "development-secret-key"


# --------------------
# HOME
# --------------------

@app.route("/")
def home():
    return "Welcome to SecureCart!"


# --------------------
# AUTHENTICATION
# --------------------

@app.route("/api/v1/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "error": "Username and password are required"
        }), 400

    password_hash = generate_password_hash(password)

    db = get_db()

    try:
        db.execute(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, "customer")
        )

        db.commit()

    except Exception:
        db.close()

        return jsonify({
            "error": "Username already exists"
        }), 409

    db.close()

    return jsonify({
        "message": "Registration successful"
    }), 201


@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "error": "Username and password are required"
        }), 400

    db = get_db()

    user = db.execute(
        """
        SELECT id, username, password_hash, role
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    db.close()

    if user is None or not check_password_hash(
        user["password_hash"],
        password
    ):
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    session["user_id"] = user["id"]

    return jsonify({
        "message": "Login successful",
        "username": user["username"],
        "role": user["role"]
    }), 200


@app.route("/api/v1/auth/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "message": "Logout successful"
    }), 200


# --------------------
# USER PROFILE
# --------------------

@app.route("/api/v1/me", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    db = get_db()

    user = db.execute(
        """
        SELECT id, username, full_name, role, created_at
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    db.close()

    if user is None:
        session.clear()

        return jsonify({
            "error": "User not found"
        }), 401

    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
        "created_at": user["created_at"]
    }), 200


@app.route("/api/v1/me", methods=["PATCH"])
def update_current_user():
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json()

    full_name = data.get("full_name")

    if not full_name:
        return jsonify({
            "error": "Full name is required"
        }), 400

    db = get_db()

    db.execute(
        """
        UPDATE users
        SET full_name = ?
        WHERE id = ?
        """,
        (full_name, user_id)
    )

    db.commit()
    db.close()

    return jsonify({
        "message": "Profile updated successfully",
        "full_name": full_name
    }), 200


# --------------------
# PRODUCTS
# --------------------

@app.route("/api/v1/products", methods=["GET"])
def get_products():
    db = get_db()

    products = db.execute(
        """
        SELECT id, name, description, price, stock
        FROM products
        ORDER BY id
        """
    ).fetchall()

    db.close()

    return jsonify([
        {
            "id": product["id"],
            "name": product["name"],
            "description": product["description"],
            "price": product["price"],
            "stock": product["stock"]
        }
        for product in products
    ]), 200


# --------------------
# ORDERS
# --------------------

@app.route("/api/v1/orders", methods=["POST"])
def create_order():
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json()

    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not quantity:
        return jsonify({
            "error": "Product ID and quantity are required"
        }), 400

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({
            "error": "Quantity must be a positive integer"
        }), 400

    db = get_db()

    product = db.execute(
        """
        SELECT id, name, price, stock
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    if product is None:
        db.close()

        return jsonify({
            "error": "Product not found"
        }), 404

    if quantity > product["stock"]:
        db.close()

        return jsonify({
            "error": "Not enough stock"
        }), 400

    # Server calculates the real total.
    total = product["price"] * quantity

    cursor = db.execute(
        """
        INSERT INTO orders (user_id, total, status)
        VALUES (?, ?, ?)
        """,
        (user_id, total, "pending")
    )

    order_id = cursor.lastrowid

    db.execute(
        """
        INSERT INTO order_items
        (order_id, product_id, quantity, price_at_purchase)
        VALUES (?, ?, ?, ?)
        """,
        (
            order_id,
            product["id"],
            quantity,
            product["price"]
        )
    )

    db.commit()
    db.close()

    return jsonify({
        "message": "Order created successfully",
        "order_id": order_id,
        "product": product["name"],
        "quantity": quantity,
        "total": total,
        "status": "pending"
    }), 201


@app.route("/api/v1/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    db = get_db()

    order = db.execute(
        """
        SELECT id, user_id, total, status, created_at
        FROM orders
        WHERE id = ?
        """,
        (order_id,)
    ).fetchone()

    if order is None:
        db.close()

        return jsonify({
            "error": "Order not found"
        }), 404

    # A customer can only view their own order.
    if order["user_id"] != user_id:
        db.close()

        return jsonify({
            "error": "Access denied"
        }), 403

    items = db.execute(
        """
        SELECT
            products.name,
            order_items.quantity,
            order_items.price_at_purchase
        FROM order_items
        JOIN products
            ON order_items.product_id = products.id
        WHERE order_items.order_id = ?
        """,
        (order_id,)
    ).fetchall()

    db.close()

    return jsonify({
        "id": order["id"],
        "total": order["total"],
        "status": order["status"],
        "created_at": order["created_at"],
        "items": [
            {
                "product": item["name"],
                "quantity": item["quantity"],
                "price": item["price_at_purchase"]
            }
            for item in items
        ]
    }), 200


# --------------------
# START APPLICATION
# --------------------

if __name__ == "__main__":
    init_db()
    app.run(debug=True)




    