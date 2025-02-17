import os
import shelve
from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt

admin_createaccount_bp = Blueprint('createaccount', __name__)
bcrypt = Bcrypt()

DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH = os.path.join(DB_FOLDER, "accounts")

@admin_createaccount_bp.route('/createaccounts', methods=['POST'])
def create_account():
    data = request.json

    # Validate input
    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "All fields are required"}), 400

    with shelve.open(DB_PATH, writeback=True) as db:
        # Check for duplicate email
        for account in db.values():
            if account["email"] == data["email"]:
                return jsonify({"error": "Email already exists"}), 400

        # Generate a new unique ID
        account_id = str(len(db) + 1)

        # Hash password with bcrypt
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        # Create new user object
        new_account = {
            "id": account_id,
            "username": data['name'],
            "email": data['email'],
            "password": hashed_password,  # Securely hashed password
            "role": "user",  # Default role
            "status": "active",  # User is active by default
            "failed_attempts": 0,  # Track failed login attempts
            "disabled": False,  # Keep existing structure
            "disabled_until": None,  # Keep existing structure
        }

        # Save to database
        db[account_id] = new_account

    return jsonify({
        "message": "Account created successfully",
        "account": {"id": account_id, "username": data['name'], "email": data['email']}
    }), 201