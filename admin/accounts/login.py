from flask import Blueprint, jsonify, request
import os
import shelve
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
import datetime
import uuid

# Initialize Blueprint
admin_auth_bp = Blueprint("admin_auth", __name__)
bcrypt = Bcrypt()

# Database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts")

@admin_auth_bp.route("/login", methods=['POST'])
def admin_login():
    """
    Admin login route that ensures only users with 'admin' role can log in.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid request: No JSON received"}), 400

        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not email or not password:
            return jsonify({"error": "Missing email or password"}), 400

        with shelve.open(DB_PATH_ACCOUNTS) as db:
            user = next((user for user in db.values() if user.get("email") == email), None)

        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        # ✅ Verify the password
        if not bcrypt.check_password_hash(user["password"], password):
            return jsonify({"error": "Invalid email or password"}), 401

        # ✅ Ensure the user is an admin
        if user.get("role") != "admin":
            return jsonify({"error": "Access denied. Admins only."}), 403

        # ✅ Generate a new JWT token for the admin
        expires = datetime.timedelta(hours=24)  # 24-hour expiration
        token = create_access_token(
            identity={"id": user["id"], "username": user["username"], "role": "admin"},
            expires_delta=expires,  # Explicitly set expiry
            additional_claims={"jti": str(uuid.uuid4())}  # Ensures uniqueness
        )

        return jsonify({"token": token}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
@admin_auth_bp.route("/auth/me", methods=["GET"])
@jwt_required
def get_current_user():
    print("PLS")
    current_user = get_jwt_identity()
    return jsonify(current_user), 200