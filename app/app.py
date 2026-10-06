from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db, init_db

app = Flask(__name__)

app.secret_key = "development-secret-key"


@app.route("/")
def home():
    return "Welcome to SecureCart!"


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


if __name__ == "__main__":
    init_db()
    app.run(debug=True)


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
        SELECT id, username, role, created_at
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
        "role": user["role"],
        "created_at": user["created_at"]
    }), 200