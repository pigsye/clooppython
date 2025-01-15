import os
import shelve
from flask import Blueprint, jsonify, request

logs_bp = Blueprint("logs", __name__, url_prefix="/api/logs")

DB_FOLDER = os.path.join(os.path.dirname(__file__), "db")
DB_PATH_LOGS = os.path.join(DB_FOLDER, "logs")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts")


@logs_bp.route("/", methods=["GET"])
def get_all_logs():
    """
    Get a summary of all chat logs.
    """
    try:
        logs_summary = []
        with shelve.open(DB_PATH_LOGS) as logs_db, shelve.open(DB_PATH_ACCOUNTS) as accounts_db:
            for log_id, log in logs_db.items():
                user1 = accounts_db.get(str(log["user1"]), {}).get("username", "Unknown User")
                user2 = accounts_db.get(str(log["user2"]), {}).get("username", "Unknown User")
                logs_summary.append({
                    "id": log_id,
                    "user1": user1,
                    "user2": user2,
                })
        return jsonify(logs_summary), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@logs_bp.route("/<int:log_id>", methods=["GET"])
def get_chat_log(log_id):
    """
    Get details of a specific chat log.
    """
    try:
        with shelve.open(DB_PATH_LOGS) as logs_db, shelve.open(DB_PATH_ACCOUNTS) as accounts_db:
            chat_log = logs_db.get(str(log_id))
            if not chat_log:
                return jsonify({"error": "Log not found"}), 404

            user1 = accounts_db.get(str(chat_log["user1"]), {}).get("username", "Unknown User")
            user2 = accounts_db.get(str(chat_log["user2"]), {}).get("username", "Unknown User")

            response = {
                "user1": user1,
                "user2": user2,
                "logs": chat_log["logs"]
            }
            return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@logs_bp.route("/create", methods=["POST"])
def create_chat_log():
    """
    Create a new chat log between two users.
    """
    try:
        data = request.json
        user1 = data.get("user1")
        user2 = data.get("user2")

        if not user1 or not user2:
            return jsonify({"error": "Both user1 and user2 are required"}), 400

        # Validate users exist
        with shelve.open(DB_PATH_ACCOUNTS) as accounts_db:
            if str(user1) not in accounts_db or str(user2) not in accounts_db:
                return jsonify({"error": "One or both users do not exist"}), 404

        with shelve.open(DB_PATH_LOGS, writeback=True) as logs_db:
            # Generate a new log ID
            new_log_id = max((int(k) for k in logs_db.keys()), default=0) + 1

            # Create the new chat log entry
            logs_db[str(new_log_id)] = {
                "user1": user1,
                "user2": user2,
                "logs": [],  # Empty chat log
            }

        return jsonify({
            "message": "Chat log created successfully!",
            "log_id": new_log_id,
            "user1": user1,
            "user2": user2,
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@logs_bp.route('/<int:log_id>', methods=['DELETE'])
def delete_chat_log(log_id):
    """
    Delete a specific chat log by its ID.
    """
    try:
        with shelve.open(DB_PATH_LOGS, writeback=True) as logs_db:
            if str(log_id) not in logs_db:
                return jsonify({"error": "Chat log not found"}), 404

            del logs_db[str(log_id)]  # Remove the log from the database

        return jsonify({"message": "Chat log deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@logs_bp.route('/<int:log_id>/update_users', methods=['POST'])
def update_chat_users(log_id):
    """
    Update the users in a specific chat log.
    """
    try:
        data = request.json
        user1_id = data.get("user1")
        user2_id = data.get("user2")

        if not user1_id or not user2_id:
            return jsonify({"error": "Both user IDs are required"}), 400

        with shelve.open(DB_PATH_LOGS, writeback=True) as logs_db, shelve.open(DB_PATH_ACCOUNTS) as accounts_db:
            if str(log_id) not in logs_db:
                return jsonify({"error": "Chat log not found"}), 404

            # Validate the new users exist in the accounts database
            if str(user1_id) not in accounts_db:
                return jsonify({"error": f"User with ID {user1_id} not found"}), 404
            if str(user2_id) not in accounts_db:
                return jsonify({"error": f"User with ID {user2_id} not found"}), 404

            # Update the chat log
            log = logs_db[str(log_id)]
            log["user1"] = int(user1_id)
            log["user2"] = int(user2_id)
            logs_db[str(log_id)] = log

        return jsonify({"message": "Chat log users updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500