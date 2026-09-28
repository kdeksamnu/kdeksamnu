import os
import sqlite3
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, g

app = Flask(__name__)
# Uses the environment variable you fixed previously, or falls back to a default
JWT_SECRET = os.environ.get("JWT_SECRET", "super-secret-key")

def get_db():
    db = sqlite3.connect("recipes.db") 
    db.row_factory = sqlite3.Row
    return db

# --- Authentication Middleware ---
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            # Cast to string to prevent subject validation mismatches
            g.user_id = str(payload["sub"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
            
        return f(*args, **kwargs)
    return decorated

# --- Routes ---

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    db = get_db()
    try:
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                  (data["username"], data["password"]))
        db.commit()
        return jsonify({"message": "User created"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "User already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                     (data["username"], data["password"])).fetchone()
    if user:
        token = jwt.encode({
            "sub": str(user["id"]),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET, algorithm="HS256")
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/recipes", methods=["POST"])
@require_auth
def create_recipe():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO recipes (title, is_public, user_id) VALUES (?, ?, ?)", 
                   (data.get("title"), data.get("is_public", 0), g.user_id))
    db.commit()
    return jsonify({"message": "Recipe created", "id": cursor.lastrowid}), 201

@app.route("/recipes/<int:recipe_id>", methods=["GET"])
def get_recipe(recipe_id):
    db = get_db()
    recipe = db.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if recipe:
        return jsonify(dict(recipe)), 200
    return jsonify({"error": "Not found"}), 404

@app.route("/recipes/<int:recipe_id>", methods=["PUT"])
@require_auth
def update_recipe(recipe_id):
    db = get_db()
    recipe = db.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404
        
    if str(recipe["user_id"]) != g.user_id:
        return jsonify({"error": "Forbidden - You do not own this recipe"}), 403
        
    data = request.json
    db.execute("UPDATE recipes SET title = ?, is_public = ? WHERE id = ?", 
               (data.get("title"), data.get("is_public", recipe["is_public"]), recipe_id))
    db.commit()
    return jsonify({"message": "Recipe updated"}), 200

@app.route("/recipes/<int:recipe_id>", methods=["DELETE"])
@require_auth
def delete_recipe(recipe_id):
    db = get_db()
    recipe = db.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404
        
    if str(recipe["user_id"]) != g.user_id:
        return jsonify({"error": "Forbidden - You do not own this recipe"}), 403
        
    db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    db.commit()
    return '', 204

if __name__ == "__main__":
    app.run(debug=True, port=5000)
