import os
import json
from flask import Blueprint, jsonify, request

admin_clothings_bp = Blueprint("clothing", __name__, url_prefix="/clothing")

DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_SUBMISSIONS = os.path.join(DB_FOLDER, "submissions.json")
DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products.json")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts.json")

def load_json(db_path):
    if not os.path.exists(db_path):
        return {}
    with open(db_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(db_path, data):
    with open(db_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@admin_clothings_bp.route('/submissions', methods=['GET'])
def get_submissions():
    try:
        submissions_db = load_json(DB_PATH_SUBMISSIONS)
        accounts_db = load_json(DB_PATH_ACCOUNTS)

        submissions = []
        for submission_id, submission in submissions_db.items():
            customer_id = str(submission.get("customerId"))
            customer_name = accounts_db.get(customer_id, {}).get("username", "Unknown")

            submissions.append({
                "id": submission_id,
                "customerName": customer_name,
                "clothing_name": submission.get("clothing_name"),
                "description": submission.get("description"),
                "customerId": customer_id,
            })

        return jsonify(submissions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500