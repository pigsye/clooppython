from flask import Blueprint, request, jsonify
import os
import shelve
import time

user_feedback_bp = Blueprint("user_feedback", __name__)

# Database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_FEEDBACK = os.path.join(DB_FOLDER, "feedback")

@user_feedback_bp.route("/feedback", methods=["POST"])
def submit_feedback():
    """
    Store contact form submissions in `feedback.db`.
    """
    try:
        data = request.json
        user_id = "1"  # Assume user ID 1 for now
        message = data.get("message", "").strip()

        if not message:
            return jsonify({"error": "Message is required"}), 400

        entry = {
            "user_id": user_id,
            "feedback": message
        }

        with shelve.open(DB_PATH_FEEDBACK, writeback=True) as db:
            entry_id = str(int(time.time()))  # Use timestamp as unique ID
            db[entry_id] = entry

        return jsonify({"message": "Feedback submitted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500