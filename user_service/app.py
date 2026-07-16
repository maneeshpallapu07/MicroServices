from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_FILE = "users.json"


# -----------------------------
# Utility Functions
# -----------------------------

def load_users():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)


# -----------------------------
# Health Check
# -----------------------------

@app.route("/health")
def health():
    return jsonify({"status": "UP"})


# -----------------------------
# Get All Users
# -----------------------------

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(load_users())


# -----------------------------
# Get User by ID
# -----------------------------

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):

    users = load_users()

    for user in users:
        if user["id"] == user_id:
            return jsonify(user)

    return jsonify({"message": "User Not Found"}), 404


# -----------------------------
# Add User
# -----------------------------

@app.route("/users", methods=["POST"])
def add_user():

    users = load_users()

    data = request.json

    new_user = {
        "id": len(users) + 1,
        "name": data["name"],
        "email": data["email"]
    }

    users.append(new_user)

    save_users(users)

    return jsonify({
        "message": "User Created",
        "user": new_user
    }), 201


# -----------------------------
# Update User
# -----------------------------

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):

    users = load_users()

    data = request.json

    for user in users:

        if user["id"] == user_id:

            user["name"] = data["name"]
            user["email"] = data["email"]

            save_users(users)

            return jsonify(user)

    return jsonify({"message": "User Not Found"}), 404


# -----------------------------
# Delete User
# -----------------------------

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):

    users = load_users()

    for user in users:

        if user["id"] == user_id:

            users.remove(user)

            save_users(users)

            return jsonify({
                "message": "User Deleted"
            })

    return jsonify({"message": "User Not Found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
