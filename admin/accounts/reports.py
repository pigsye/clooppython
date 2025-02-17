import os
import shelve
from flask import Blueprint, jsonify, request
import time

admin_reports_bp = Blueprint('reports', __name__)

# Define the path to the database folder
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")

# Define paths to individual database files
DB_PATH_REPORT = os.path.join(DB_FOLDER, "reports")
DB_PATH_ACCOUNT = os.path.join(DB_FOLDER, "accounts")


@admin_reports_bp.route('/reports', methods=['GET'])
def get_reports():
    try:
        account_usernames = {}
        with shelve.open(DB_PATH_ACCOUNT) as accounts_db:
            for user_id, account in accounts_db.items():
                account_usernames[user_id] = account.get("username", f"User {user_id}")

        reports = []
        with shelve.open(DB_PATH_REPORT) as reports_db:
            for report_id, report in reports_db.items():
                reports.append({
                    "id": report_id,  # Include the report ID
                    "customerId": report.get("customerId"),
                    "customerName": account_usernames.get(report.get("customerId"), "Unknown"),
                    "reportedBy": account_usernames.get(report.get("reportedBy"), "Unknown"),
                    "reason": report.get("reason", "No reason provided"),
                })
        return jsonify(reports), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_reports_bp.route('/reports/deletereport', methods=['POST'])
def delete_report():
    try:
        # Parse the JSON payload
        data = request.json
        report_id = data.get("reportId")

        if not report_id:
            return jsonify({"error": "Missing report ID"}), 400

        with shelve.open(DB_PATH_REPORT, writeback=True) as reports_db:
            if report_id in reports_db:
                del reports_db[report_id]  # Remove the report
                return jsonify({"message": "Report deleted successfully"}), 200
            else:
                return jsonify({"error": "Report not found"}), 404

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@admin_reports_bp.route('/reports/actonreport', methods=['POST'])
def act_on_report():
    """
    Disable the user associated with a report and delete the report.
    """
    try:
        # Parse the request JSON
        data = request.json
        report_id = data.get("reportId")
        duration = data.get("duration")

        if not report_id or not duration:
            return jsonify({"error": "Missing report ID or duration"}), 400

        with shelve.open(DB_PATH_REPORT, writeback=True) as reports_db:
            report = reports_db.get(report_id)

            if not report:
                return jsonify({"error": "Report not found"}), 404

            customer_id = report.get("customerId")

            # Disable the user in accounts.db
            with shelve.open(DB_PATH_ACCOUNT, writeback=True) as accounts_db:
                if str(customer_id) not in accounts_db:
                    return jsonify({"error": "User not found"}), 404

                user_account = accounts_db[str(customer_id)]
                user_account["disabled"] = True
                user_account["disabled_until"] = int(time.time()) + int(duration)
                accounts_db[str(customer_id)] = user_account

            # Delete the report
            del reports_db[report_id]

        return jsonify({"message": "User disabled and report deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@admin_reports_bp.route('/reports/create', methods=['POST'])
def create_report():
    """
    Create a new report in the database.
    """
    try:
        data = request.json
        customer_id = data.get("customerId")
        reported_by = data.get("reportedBy")
        reason = data.get("reason")

        if not customer_id or not reported_by or not reason:
            return jsonify({"error": "Missing required fields."}), 400

        # Generate a unique report ID
        report_id = str(int(time.time()))

        # Save the report in the database
        with shelve.open(DB_PATH_REPORT, writeback=True) as reports_db:
            reports_db[report_id] = {
                "customerId": customer_id,
                "reportedBy": reported_by,
                "reason": reason
            }

        return jsonify({"message": "Report created successfully!", "report": {
            "id": report_id,
            "customerId": customer_id,
            "reportedBy": reported_by,
            "reason": reason,
        }}), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@admin_reports_bp.route('/reports/edit', methods=['POST'])
def edit_report():
    """
    Edit an existing report's details.
    """
    try:
        data = request.json
        report_id = data.get("reportId")
        customer_id = data.get("customerId")
        reported_by = data.get("reportedBy")
        reason = data.get("reason")

        if not all([report_id, customer_id, reported_by, reason]):
            return jsonify({"error": "All fields are required"}), 400

        with shelve.open(DB_PATH_REPORT, writeback=True) as reports_db:
            report = reports_db.get(report_id)
            if not report:
                return jsonify({"error": "Report not found"}), 404

            # Update report details
            report["customerId"] = customer_id
            report["reportedBy"] = reported_by
            report["reason"] = reason
            reports_db[report_id] = report

        return jsonify({"message": "Report updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500