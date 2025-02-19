import os
import json
from flask import Blueprint, jsonify, request

admin_logs_bp = Blueprint("logs", __name__)

DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_LOGS = os.path.join(DB_FOLDER, "logs.json")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts.json")

def load_json(db_path):
    if not os.path.exists(db_path):
        return {}
    with open(db_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(db_path, data):
    with open(db_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@admin_logs_bp.route("/logs", methods=["GET"])
def get_all_logs():
    try:
        logs_db = load_json(DB_PATH_LOGS)
        accounts_db = load_json(DB_PATH_ACCOUNTS)

        logs_summary = [
            {
                "id": log_id,
                "user1": accounts_db.get(str(log["user1"]), {}).get("username", "Unknown"),
                "user2": accounts_db.get(str(log["user2"]), {}).get("username", "Unknown"),
            }
            for log_id, log in logs_db.items()
        ]

        return jsonify(logs_summary), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_logs_bp.route("/logs/create", methods=["POST"])
def create_chat_log():
    try:
        data = request.json
        user1 = str(data.get("user1"))
        user2 = str(data.get("user2"))

        if not user1 or not user2:
            return jsonify({"error": "Both user1 and user2 are required"}), 400

        logs_db = load_json(DB_PATH_LOGS)
        new_log_id = str(max([int(k) for k in logs_db.keys()] or [0]) + 1)

        logs_db[new_log_id] = {
            "user1": user1,
            "user2": user2,
            "logs": [],
        }

        save_json(DB_PATH_LOGS, logs_db)

        return jsonify({"message": "Chat log created successfully!", "log_id": new_log_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500