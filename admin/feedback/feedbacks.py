import os
import json
from flask import Blueprint, jsonify, request

admin_feedbacks_bp = Blueprint('feedback', __name__)

# Define database paths
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_FEEDBACK = os.path.join(DB_FOLDER, "feedback.json")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts.json")

def load_json(db_path):
    if not os.path.exists(db_path):
        return {}
    with open(db_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(db_path, data):
    with open(db_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@admin_feedbacks_bp.route('/feedback', methods=['GET'])
def get_all_feedbacks():
    try:
        feedback_db = load_json(DB_PATH_FEEDBACK)
        accounts_db = load_json(DB_PATH_ACCOUNTS)

        feedback_list = [
            {
                "id": feedback_id,
                "user_id": feedback["user_id"],
                "username": accounts_db.get(str(feedback["user_id"]), {}).get("username", "Unknown"),
                "feedback": feedback["feedback"],
            }
            for feedback_id, feedback in feedback_db.items()
        ]

        return jsonify(feedback_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_feedbacks_bp.route('/feedback/create', methods=['POST'])
def create_feedback():
    try:
        data = request.json
        user_id = str(data.get("user_id"))
        feedback_text = data.get("feedback")

        if not user_id or not feedback_text:
            return jsonify({"error": "User ID and feedback are required"}), 400

        feedback_db = load_json(DB_PATH_FEEDBACK)
        new_feedback_id = str(max([int(k) for k in feedback_db.keys()] or [0]) + 1)

        feedback_db[new_feedback_id] = {
            "user_id": user_id,
            "feedback": feedback_text,
        }

        save_json(DB_PATH_FEEDBACK, feedback_db)

        return jsonify({"message": "Feedback created successfully!", "feedback_id": new_feedback_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500