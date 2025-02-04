import os
import shelve
from flask import Blueprint, request, jsonify
import hashlib

admin_createaccount_bp = Blueprint('createaccount', __name__)

# Define the path to the database folder and accounts database file
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH = os.path.join(DB_FOLDER, "accounts")

@admin_createaccount_bp.route('/createaccounts', methods=['POST'])
def create_account():
    data = request.json

    # Validate input
    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "All fields are required"}), 400

    with shelve.open(DB_PATH) as db:
        # Check for duplicate email
        for account in db.values():
            if account["email"] == data["email"]:
                return jsonify({"error": "Email already exists"}), 400

        # Generate a new unique ID
        account_id = str(len(db) + 1)

        # Create account object
        new_account = {
            "id": account_id,
            "username": data['name'],
            "email": data['email'],
            "disabled": False,
            "disabled_until": None,
            "password": hashlib.sha256(data['password'].encode()).hexdigest()  # Store hashed passwords in production
        }

        info_to_send_back = {
            "id": account_id,
            "username": data['name'],
            "email": data['email']
        }

        # Save to Shelve
        db[account_id] = new_account

    return jsonify({"message": "Account created successfully", "account": info_to_send_back}), 201