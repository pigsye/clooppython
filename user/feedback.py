from flask import Blueprint, request, jsonify
import os
import json
import time

user_feedback_bp = Blueprint("user_feedback", __name__)

# Database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_FEEDBACK = os.path.join(DB_FOLDER, "feedback.json")

def load_json(db_path):
    """Load JSON data from a file."""
    if not os.path.exists(db_path):
        return {}
    with open(db_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(db_path, data):
    """Save JSON data to a file."""
    with open(db_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@user_feedback_bp.route("/feedback", methods=["POST"])
def submit_feedback():
    """
    Store contact form submissions in `feedback.json`.
    """
    try:
        data = request.json
        user_id = "1"  # Assume user ID 1 for now
        message = data.get("message", "").strip()

        if not message:
            return jsonify({"error": "Message is required"}), 400

        feedback_db = load_json(DB_PATH_FEEDBACK)

        entry_id = str(int(time.time()))  # Use timestamp as unique ID
        feedback_db[entry_id] = {
            "user_id": user_id,
            "feedback": message
        }

        save_json(DB_PATH_FEEDBACK, feedback_db)

        return jsonify({"message": "Feedback submitted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500