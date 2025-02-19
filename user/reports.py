from flask import Blueprint, request, jsonify
import os
import json
from flask_jwt_extended import jwt_required, get_jwt_identity

user_reports_bp = Blueprint("user_reports", __name__)

# Database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_REPORTS = os.path.join(DB_FOLDER, "reports.json")

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

@user_reports_bp.route("/report-user/<int:user_id>", methods=["POST"])
@jwt_required()
def report_user(user_id):
    """
    Allows a logged-in user to report another user.
    The report is stored in the reports database.
    """
    try:
        reporter = str(get_jwt_identity()["id"])  # Get logged-in user ID
        data = request.json
        reason = data.get("reason", "").strip()

        if not reason:
            return jsonify({"error": "Report reason is required"}), 400

        if reporter == str(user_id):
            return jsonify({"error": "You cannot report yourself"}), 403

        reports_db = load_json(DB_PATH_REPORTS)

        # Generate a new unique report ID
        report_id = str(len(reports_db) + 1)

        reports_db[report_id] = {
            "id": report_id,
            "customerId": str(user_id),
            "reportedBy": reporter,
            "reason": reason
        }

        save_json(DB_PATH_REPORTS, reports_db)

        return jsonify({"message": "Report submitted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500