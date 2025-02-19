import os
import json
import time
from flask import Blueprint, request, jsonify

admin_account_status_bp = Blueprint("account_status", __name__)

# ✅ Database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_ACCOUNT = os.path.join(DB_FOLDER, "accounts.json")

def load_json(db_path):
    """Load JSON file and return a dictionary."""
    if not os.path.exists(db_path):
        return {}  # Return an empty dictionary if the file doesn't exist
    with open(db_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(db_path, data):
    """Save dictionary data to JSON file."""
    with open(db_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

@admin_account_status_bp.route("/accountstatus/<int:user_id>", methods=["POST"])
def update_account_status(user_id):
    """
    Update the status of a user's account (enable or disable).
    """
    try:
        data = request.json
        action = data.get("function")  # "enable" or "disable"
        duration = data.get("duration", None)  # Duration for disabling in seconds (optional)

        if action not in ["enable", "disable"]:
            return jsonify({"error": "Invalid function. Must be 'enable' or 'disable'"}), 400

        accounts_db = load_json(DB_PATH_ACCOUNT)  # ✅ Load JSON database
        user_key = str(user_id)

        if user_key not in accounts_db:
            return jsonify({"error": "User not found"}), 404

        user_data = accounts_db[user_key]
        username = user_data.get("username", "Unknown User")

        if action == "disable":
            if not duration:
                return jsonify({"error": "Duration is required for disabling an account"}), 400

            # Disable the user and set the disabled_until timestamp
            user_data["disabled"] = True
            user_data["disabled_until"] = int(time.time()) + int(duration)
            message = f"{username} disabled for {duration} seconds."

        elif action == "enable":
            # Enable the user by resetting the disabled status and timestamp
            user_data["disabled"] = False
            user_data["disabled_until"] = None
            message = f"{username} enabled successfully."

        # ✅ Write changes back to JSON file
        accounts_db[user_key] = user_data
        save_json(DB_PATH_ACCOUNT, accounts_db)

        return jsonify({"message": message}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500