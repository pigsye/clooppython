import os
import json
import time
from flask import Blueprint, jsonify, request

admin_reports_bp = Blueprint("reports", __name__)

# Define the path to the database folder
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")

# Define paths to individual database files
DB_PATH_REPORTS = os.path.join(DB_FOLDER, "reports.json")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts.json")

def load_json(db_path):
    """Load JSON data from file."""
    if not os.path.exists(db_path):
        return {}
    with open(db_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(db_path, data):
    """Save JSON data to file."""
    with open(db_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@admin_reports_bp.route("/reports", methods=["GET"])
def get_reports():
    """Retrieve all reports."""
    try:
        accounts_db = load_json(DB_PATH_ACCOUNTS)
        reports_db = load_json(DB_PATH_REPORTS)

        reports = []
        for report_id, report in reports_db.items():
            reports.append({
                "id": report_id,
                "customerId": report.get("customerId"),
                "customerName": accounts_db.get(report.get("customerId"), {}).get("username", "Unknown"),
                "reportedBy": accounts_db.get(report.get("reportedBy"), {}).get("username", "Unknown"),
                "reason": report.get("reason", "No reason provided"),
            })

        return jsonify(reports), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_reports_bp.route("/reports/deletereport", methods=["POST"])
def delete_report():
    """Delete a report."""
    try:
        data = request.json
        report_id = str(data.get("reportId"))

        if not report_id:
            return jsonify({"error": "Missing report ID"}), 400

        reports_db = load_json(DB_PATH_REPORTS)

        if report_id in reports_db:
            del reports_db[report_id]
            save_json(DB_PATH_REPORTS, reports_db)
            return jsonify({"message": "Report deleted successfully"}), 200

        return jsonify({"error": "Report not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_reports_bp.route("/reports/create", methods=["POST"])
def create_report():
    """Create a new report."""
    try:
        data = request.json
        customer_id = str(data.get("customerId"))
        reported_by = str(data.get("reportedBy"))
        reason = data.get("reason")

        if not customer_id or not reported_by or not reason:
            return jsonify({"error": "Missing required fields."}), 400

        report_id = str(int(time.time()))
        reports_db = load_json(DB_PATH_REPORTS)

        reports_db[report_id] = {
            "customerId": customer_id,
            "reportedBy": reported_by,
            "reason": reason
        }

        save_json(DB_PATH_REPORTS, reports_db)

        return jsonify({"message": "Report created successfully!", "report": reports_db[report_id]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500