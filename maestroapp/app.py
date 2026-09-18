from flask import Flask, request, jsonify

app = Flask(__name__)

# Simulated user database for our audit loop
users_db = {}

@app.post("/register")
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    if username in users_db:
        return jsonify({"error": "Username already exists"}), 409

    users_db[username] = password
    return jsonify({"message": "User created successfully"}), 201

@app.post("/login")
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    # Bad input: Missing required fields -> 400 Bad Request
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # Auth failure: Unknown user or incorrect password -> 401 Unauthorized
    if username not in users_db or users_db[username] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
