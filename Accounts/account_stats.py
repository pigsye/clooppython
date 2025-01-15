import os
import shelve
import time
from flask import Blueprint, request, jsonify

account_status_bp = Blueprint("account_status", __name__, url_prefix="/api")

# Database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_ACCOUNT = os.path.join(DB_FOLDER, "accounts")


@account_status_bp.route("/accountstatus/<int:user_id>", methods=["POST"])
def update_account_status(user_id):
    """
    Update the status of a user's account (enable or disable).
    """
    try:
        # Parse JSON request
        data = request.json
        action = data.get("function")  # "enable" or "disable"
        duration = data.get("duration", None)  # Duration for disabling in seconds (optional)

        if action not in ["enable", "disable"]:
            return jsonify({"error": "Invalid function. Must be 'enable' or 'disable'"}), 400

        with shelve.open(DB_PATH_ACCOUNT, writeback=True) as db:
            user_key = str(user_id)

            if user_key not in db:
                return jsonify({"error": "User not found"}), 404

            user_data = db[user_key]
            username = user_data.get("username", "Unknown User")

            user_data = db[user_key]

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

            # Write changes back to the database
            db[user_key] = user_data
            db.sync()

        return jsonify({"message": message}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500