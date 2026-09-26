from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, jsonify, request
import jwt

app = Flask(__name__)
SECRET_KEY = "your-secret-key"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired, please log in again'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated
@app.route("/test-login", methods=["POST"])
def test_login():
    # fake user row just for testing
    user_row = {"id": 1, "username": "testuser"}
    token = create_access_token(user_row)
    return jsonify({"access_token": token})
@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    return jsonify({'message': f'Access granted for user {current_user}'})

if __name__ == '__main__':
    app.run(debug=True)

"""Recipe Box API — BE104 course skeleton.

A working Flask + SQLite CRUD API for recipes with JWT signature verification.
"""

import os
import sqlite3
from datetime import datetime, timedelta
import jwt
from jwt import InvalidTokenError

from flask import Flask, g, jsonify, request

DATABASE = "recipes.db"
JWT_SECRET = os.environ.get("JWT_SECRET", "super-secret-key")

app = Flask(__name__)


def create_access_token(user_row):
    now = datetime.utcnow()
    payload = {
        "sub": user_row["id"],
        "username": user_row["username"],
        # TEMP: short expiry for testing
        "exp": now + timedelta(seconds=10),
    }


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/recipes", methods=["GET"])
def get_recipes():
    db = get_db()
    cursor = db.execute("SELECT * FROM recipes")
    recipes = [dict(row) for row in cursor.fetchall()]
    return jsonify(recipes), 200


@app.route("/recipes", methods=["POST"])
def create_recipe():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header[len("Bearer "):].strip()
    try:
        claims = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except InvalidTokenError:
        return jsonify({"error": "Invalid or tampered token"}), 401

    # claims now holds the verified payload (sub, username, etc.)
    data = request.get_json() or {}
    title = data.get("title")
    ingredients = data.get("ingredients")
    instructions = data.get("instructions")

    if not title or not ingredients or not instructions:
        return jsonify({"error": "Missing required fields"}), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)",
        (title, ingredients, instructions)
    )
    db.commit()
    return jsonify({"id": cursor.lastrowid, "title": title}), 201


if __name__ == "__main__":
    app.run(debug=True, port=5000)
