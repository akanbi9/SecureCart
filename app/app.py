from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import requests

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

def get_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        return None

    db = get_db()

    user = db.execute(
        """
        SELECT id, username, role
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    db.close()

    return user


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

@app.route("/api/v1/admin/products", methods=["POST"])
def create_product():
    user = get_logged_in_user()

    if user is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    if user["role"] != "admin":
        return jsonify({
            "error": "Admin access required"
        }), 403

    data = request.get_json()

    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    stock = data.get("stock")

    if not name or price is None or stock is None:
        return jsonify({
            "error": "Name, price and stock are required"
        }), 400

    if not isinstance(price, (int, float)) or price <= 0:
        return jsonify({
            "error": "Price must be greater than zero"
        }), 400

    if not isinstance(stock, int) or stock < 0:
        return jsonify({
            "error": "Stock must be a non-negative integer"
        }), 400

    db = get_db()

    cursor = db.execute(
        """
        INSERT INTO products (name, description, price, stock)
        VALUES (?, ?, ?, ?)
        """,
        (name, description, price, stock)
    )

    product_id = cursor.lastrowid

    db.commit()
    db.close()

    return jsonify({
        "message": "Product created successfully",
        "product_id": product_id
    }), 201

@app.route("/api/v1/admin/products/<int:product_id>", methods=["PATCH"])
def update_product(product_id):
    user = get_logged_in_user()

    if user is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    if user["role"] != "admin":
        return jsonify({
            "error": "Admin access required"
        }), 403

    data = request.get_json()

    db = get_db()

    product = db.execute(
        """
        SELECT id, name, description, price, stock
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

    name = data.get("name", product["name"])
    description = data.get("description", product["description"])
    price = data.get("price", product["price"])
    stock = data.get("stock", product["stock"])

    if not name:
        db.close()

        return jsonify({
            "error": "Product name is required"
        }), 400

    if not isinstance(price, (int, float)) or price <= 0:
        db.close()

        return jsonify({
            "error": "Price must be greater than zero"
        }), 400

    if not isinstance(stock, int) or stock < 0:
        db.close()

        return jsonify({
            "error": "Stock must be a non-negative integer"
        }), 400

    db.execute(
        """
        UPDATE products
        SET name = ?, description = ?, price = ?, stock = ?
        WHERE id = ?
        """,
        (
            name,
            description,
            price,
            stock,
            product_id
        )
    )

    db.commit()
    db.close()

    return jsonify({
        "message": "Product updated successfully",
        "product_id": product_id,
        "name": name,
        "description": description,
        "price": price,
        "stock": stock
    }), 200

#--------------------
# ADMIN: VIEW ALL ORDERS
#--------------------

@app.route("/api/v1/admin/orders/<int:order_id>/assignment", methods=["PATCH"])
def assign_order(order_id):
    user = get_logged_in_user()

    if user is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    if user["role"] != "admin":
        return jsonify({
            "error": "Admin access required"
        }), 403

    data = request.get_json()
    support_id = data.get("support_id")

    if support_id is None:
        return jsonify({
            "error": "Support ID is required"
        }), 400

    db = get_db()

    # Check that the order exists
    order = db.execute(
        """
        SELECT id
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

    # Check that the selected user really is support staff
    support_user = db.execute(
        """
        SELECT id, username, role
        FROM users
        WHERE id = ?
        """,
        (support_id,)
    ).fetchone()

    if support_user is None or support_user["role"] != "support":
        db.close()

        return jsonify({
            "error": "Valid support user required"
        }), 400

    db.execute(
        """
        UPDATE orders
        SET assigned_support_id = ?
        WHERE id = ?
        """,
        (support_id, order_id)
    )

    db.commit()
    db.close()

    return jsonify({
        "message": "Order assigned successfully",
        "order_id": order_id,
        "support_id": support_id,
        "support_username": support_user["username"]
    }), 200

#--------------------
# SUPPORT: VIEW ASSIGNED ORDERS
#--------------------

@app.route("/api/v1/support/orders/<int:order_id>", methods=["GET"])
def get_support_order(order_id):
    user = get_logged_in_user()

    if user is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    if user["role"] != "support":
        return jsonify({
            "error": "Support access required"
        }), 403

    db = get_db()

    order = db.execute(
        """
        SELECT id, user_id, total, status,
               assigned_support_id, created_at
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

    # Support can only view orders assigned to them.
    if order["assigned_support_id"] != user["id"]:
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
        "customer_id": order["user_id"],
        "total": order["total"],
        "status": order["status"],
        "assigned_support_id": order["assigned_support_id"],
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

#--------------------
#the coupon route
#--------------------

@app.route("/api/v1/orders/<int:order_id>/coupon", methods=["POST"])
def apply_coupon(order_id):
    user = get_logged_in_user()

    if user is None:
        return jsonify({"error": "Authentication required"}), 401

    if user["role"] != "customer":
        return jsonify({"error": "Customer access required"}), 403

    data = request.get_json()
    coupon_code = data.get("coupon_code")

    if coupon_code != "SECURE10":
        return jsonify({"error": "Invalid coupon code"}), 400

    db = get_db()

    # Find the order.
    order = db.execute(
        """
        SELECT id, user_id, total
        FROM orders
        WHERE id = ?
        """,
        (order_id,)
    ).fetchone()

    if order is None:
        db.close()
        return jsonify({"error": "Order not found"}), 404

    # A customer can only apply a coupon to their own order.
    if order["user_id"] != user["id"]:
        db.close()
        return jsonify({"error": "Access denied"}), 403

    # Check whether this customer has already used the promotion.
    previous_usage = db.execute(
        """
        SELECT id
        FROM coupon_usage
        WHERE user_id = ?
        """,
        (user["id"],)
    ).fetchone()

    if previous_usage is not None:
        db.close()
        return jsonify({
            "error": "Promotion has already been used by this account"
        }), 409

    original_total = order["total"]
    discount = original_total * 0.10
    new_total = original_total - discount

    db.execute(
        """
        UPDATE orders
        SET total = ?
        WHERE id = ?
        """,
        (new_total, order_id)
    )

    db.execute(
        """
        INSERT INTO coupon_usage (user_id, order_id, coupon_code)
        VALUES (?, ?, ?)
        """,
        (user["id"], order_id, coupon_code)
    )

    db.commit()
    db.close()

    return jsonify({
        "message": "Coupon applied successfully",
        "coupon_code": coupon_code,
        "original_total": original_total,
        "discount": discount,
        "new_total": new_total
    }), 200


#--------------------
# mock payment webhook
#--------------------

@app.route("/api/v1/webhooks/mock-payment", methods=["POST"])
def mock_payment_webhook():
    data = request.get_json()

    order_id = data.get("order_id")
    payment_status = data.get("payment_status")
    webhook_secret = data.get("webhook_secret")

    # Temporary local secret for our mock payment service.
    expected_secret = "securecart-local-payment-secret"

    if webhook_secret != expected_secret:
        return jsonify({
            "error": "Invalid payment notification"
        }), 401

    if order_id is None or payment_status is None:
        return jsonify({
            "error": "Order ID and payment status are required"
        }), 400

    if payment_status not in ["paid", "failed"]:
        return jsonify({
            "error": "Invalid payment status"
        }), 400

    db = get_db()

    order = db.execute(
        """
        SELECT id, status
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

    if payment_status == "paid":
        new_status = "paid"
    else:
        new_status = "payment_failed"

    db.execute(
        """
        UPDATE orders
        SET status = ?
        WHERE id = ?
        """,
        (new_status, order_id)
    )

    db.commit()
    db.close()

    return jsonify({
        "message": "Payment notification processed",
        "order_id": order_id,
        "status": new_status
    }), 200


# --------------------
# SUPPLIER INTEGRATION PREVIEW
# --------------------

@app.route("/api/v1/integrations/preview", methods=["POST"])
def supplier_preview():
    user = get_logged_in_user()

    if user is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json()
    product_id = data.get("product_id")

    if not isinstance(product_id, int) or product_id <= 0:
        return jsonify({
            "error": "Valid product ID is required"
        }), 400

    # Only our approved local supplier can be contacted.
    supplier_url = (
        f"http://127.0.0.1:5001/supplier/product/{product_id}"
    )

    try:
        response = requests.get(
            supplier_url,
            timeout=3
        )
    except requests.RequestException:
        return jsonify({
            "error": "Supplier service unavailable"
        }), 502

    if response.status_code == 404:
        return jsonify({
            "error": "Supplier product not found"
        }), 404

    if response.status_code != 200:
        return jsonify({
            "error": "Supplier request failed"
        }), 502

    return jsonify({
        "message": "Supplier preview retrieved",
        "supplier_data": response.json()
    }), 200



# --------------------
# START APPLICATION
# --------------------

if __name__ == "__main__":
    init_db()
    app.run(debug=True)




