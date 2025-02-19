import os
import json
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime
import uuid

# Initialize Blueprint
admin_auth_bp = Blueprint("admin_auth", __name__)
bcrypt = Bcrypt()

# Database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts.json")

def load_json():
    """Load accounts JSON file."""
    if not os.path.exists(DB_PATH_ACCOUNTS):
        return {}
    with open(DB_PATH_ACCOUNTS, "r", encoding="utf-8") as file:
        return json.load(file)

@admin_auth_bp.route("/login", methods=["POST"])
def admin_login():
    """Admin login route that ensures only users with 'admin' role can log in."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid request: No JSON received"}), 400

        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not email or not password:
            return jsonify({"error": "Missing email or password"}), 400

        accounts_db = load_json()
        user = next((user for user in accounts_db.values() if user.get("email") == email), None)

        if not user or not bcrypt.check_password_hash(user["password"], password):
            return jsonify({"error": "Invalid email or password"}), 401

        if user.get("role") != "admin":
            return jsonify({"error": "Access denied. Admins only."}), 403

        # ✅ Generate JWT token for admin
        expires = datetime.timedelta(hours=24)
        token = create_access_token(
            identity={"id": user["id"], "username": user["username"], "role": "admin"},
            expires_delta=expires,
            additional_claims={"jti": str(uuid.uuid4())}
        )

        return jsonify({"token": token}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@admin_auth_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Retrieve authenticated user details."""
    return jsonify(get_jwt_identity()), 200