import os
import shelve
from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt

admin_update_bp = Blueprint('update', __name__)
bcrypt = Bcrypt()  # Initialize bcrypt

# Path to the accounts database
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH = os.path.join(DB_FOLDER, "accounts")


@admin_update_bp.route('/updateinformation/<int:user_id>', methods=['POST'])
def update_information(user_id):
    try:
        # Validate input
        data = request.json
        if not data or "update" not in data or "to" not in data:
            return jsonify({"error": "Invalid request. 'update' and 'to' fields are required."}), 400

        update_field = data["update"]
        new_value = data["to"]

        # Allowed fields to update
        allowed_updates = {"username", "email", "password"}
        if update_field not in allowed_updates:
            return jsonify({"error": f"Invalid field '{update_field}'. Allowed fields are {allowed_updates}."}), 400

        # Open the database and modify the user's data
        with shelve.open(DB_PATH, writeback=True) as db:
            user_key = str(user_id)  # Convert user_id to string since shelve keys are strings
            if user_key not in db:
                return jsonify({"error": "User not found"}), 404

            # Update the field
            if update_field == "password":
                # ✅ Hash the password using bcrypt
                hashed_password = bcrypt.generate_password_hash(new_value).decode("utf-8")
                db[user_key]["password"] = hashed_password
            else:
                db[user_key][update_field] = new_value

            # Save changes
            db.sync()

        return jsonify({"message": f"{update_field.capitalize()} updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500