from flask import Blueprint, request, jsonify
import os
import shelve
from flask_jwt_extended import jwt_required, get_jwt_identity

user_reports_bp = Blueprint("user_reports", __name__)

# Database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_REPORTS = os.path.join(DB_FOLDER, "reports")

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

        with shelve.open(DB_PATH_REPORTS, writeback=True) as db:
            report_id = str(len(db) + 1)  # Generate unique report ID
            db[report_id] = {
                "id": report_id,
                "customerId": str(user_id),
                "reportedBy": reporter,
                "reason": reason
            }

        return jsonify({"message": "Report submitted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500