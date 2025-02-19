import os
import json
from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt

admin_createaccount_bp = Blueprint("createaccount", __name__)
bcrypt = Bcrypt()

DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH = os.path.join(DB_FOLDER, "accounts.json")

def load_json():
    """Load accounts JSON file."""
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(data):
    """Save data to accounts JSON file."""
    with open(DB_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@admin_createaccount_bp.route("/createaccounts", methods=["POST"])
def create_account():
    data = request.json

    # Validate input
    if not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "All fields are required"}), 400

    accounts_db = load_json()

    # Check for duplicate email
    if any(account["email"] == data["email"] for account in accounts_db.values()):
        return jsonify({"error": "Email already exists"}), 400

    # Generate a new unique ID
    account_id = str(len(accounts_db) + 1)

    # Hash password with bcrypt
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    # Create new user object
    new_account = {
        "id": account_id,
        "username": data["name"],
        "email": data["email"],
        "password": hashed_password,  # Securely hashed password
        "role": "user",  # Default role
        "status": "active",  # User is active by default
        "failed_attempts": 0,  # Track failed login attempts
        "disabled": False,  # Keep existing structure
        "disabled_until": None,  # Keep existing structure
    }

    # Save to database
    accounts_db[account_id] = new_account
    save_json(accounts_db)

    return jsonify({
        "message": "Account created successfully",
        "account": {"id": account_id, "username": data["name"], "email": data["email"]}
    }), 201