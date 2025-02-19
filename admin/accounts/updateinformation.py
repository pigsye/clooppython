import os
import json
from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt

admin_update_bp = Blueprint("update", __name__)
bcrypt = Bcrypt()

DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts.json")

def load_json(db_path):
    """Load JSON data from file."""
    if not os.path.exists(db_path):
        return {}
    with open(db_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(db_path, data):
    """Save JSON data to file."""
    with open(db_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@admin_update_bp.route("/updateinformation/<int:user_id>", methods=["POST"])
def update_information(user_id):
    """Update user information."""
    try:
        data = request.json
        if not data or "update" not in data or "to" not in data:
            return jsonify({"error": "Invalid request. 'update' and 'to' fields are required."}), 400

        update_field = data["update"]
        new_value = data["to"]

        allowed_updates = {"username", "email", "password"}
        if update_field not in allowed_updates:
            return jsonify({"error": f"Invalid field '{update_field}'. Allowed fields are {allowed_updates}."}), 400

        accounts_db = load_json(DB_PATH_ACCOUNTS)

        user_key = str(user_id)
        if user_key not in accounts_db:
            return jsonify({"error": "User not found"}), 404

        if update_field == "password":
            hashed_password = bcrypt.generate_password_hash(new_value).decode("utf-8")
            accounts_db[user_key]["password"] = hashed_password
        else:
            accounts_db[user_key][update_field] = new_value

        save_json(DB_PATH_ACCOUNTS, accounts_db)

        return jsonify({"message": f"{update_field.capitalize()} updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500