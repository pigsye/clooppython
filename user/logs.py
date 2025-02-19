from flask import Blueprint, request, jsonify
import os
import json
import time
from flask_jwt_extended import jwt_required, get_jwt_identity

user_logs_bp = Blueprint("user_logs", __name__)

# Database paths
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_LOGS = os.path.join(DB_FOLDER, "logs.json")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts.json")

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

def get_username(user_id):
    """Fetch username from accounts database."""
    accounts_db = load_json(DB_PATH_ACCOUNTS)
    return accounts_db.get(str(user_id), {}).get("username", f"User {user_id}")

@user_logs_bp.route("/chats", methods=["GET"])
@jwt_required()  # Ensure user is logged in
def get_chats():
    """Fetch all chats for the logged-in user."""
    try:
        user_id = str(get_jwt_identity().get("id"))  # Extract user ID from JWT
        logs_db = load_json(DB_PATH_LOGS)
        user_chats = {}

        for chat_id, log in logs_db.items():
            if str(log["user1"]) == user_id or str(log["user2"]) == user_id:
                other_user_id = str(log["user2"]) if str(log["user1"]) == user_id else str(log["user1"])
                other_username = get_username(other_user_id)

                user_chats[other_user_id] = {
                    "user_id": other_user_id,
                    "username": other_username,
                    "logs": sorted(log["logs"], key=lambda x: x["timestamp"])
                }

        return jsonify({"chats": user_chats}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_logs_bp.route("/chats/<int:user2>", methods=["GET", "POST"])
@jwt_required()
def chat_logs(user2):
    """Fetch messages or send messages in chat."""
    try:
        user1 = str(get_jwt_identity().get("id"))
        logs_db = load_json(DB_PATH_LOGS)

        if request.method == "GET":
            chat_key = next((key for key, log in logs_db.items() if {str(log["user1"]), str(log["user2"])} == {user1, str(user2)}), None)

            if not chat_key:
                return jsonify({"logs": []}), 200  # No messages found

            logs = logs_db[chat_key]["logs"]
            logs.sort(key=lambda x: x["timestamp"])
            return jsonify({"logs": logs}), 200

        elif request.method == "POST":
            data = request.json
            message = data.get("message", "").strip()

            if not message:
                return jsonify({"error": "Message is required"}), 400

            chat_key = next((key for key, log in logs_db.items() if {str(log["user1"]), str(log["user2"])} == {user1, str(user2)}), None)

            new_message = {
                "user": user1,
                "timestamp": time.time(),
                "message": message
            }

            if chat_key:
                logs_db[chat_key]["logs"].append(new_message)
            else:
                chat_key = str(len(logs_db) + 1)
                logs_db[chat_key] = {"user1": user1, "user2": str(user2), "logs": [new_message]}

            save_json(DB_PATH_LOGS, logs_db)
            return jsonify({"message": "Message sent successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_logs_bp.route("/start-chat/<int:user2>", methods=["POST"])
@jwt_required()
def start_chat(user2):
    """Create a new chat between logged-in user and another user."""
    try:
        user1 = str(get_jwt_identity().get("id"))
        logs_db = load_json(DB_PATH_LOGS)

        chat_key = next((key for key, chat in logs_db.items() if {str(chat["user1"]), str(chat["user2"])} == {user1, str(user2)}), None)

        if chat_key:
            return jsonify({"message": "Chat already exists", "chat_id": chat_key}), 200

        new_chat_id = str(len(logs_db) + 1)
        logs_db[new_chat_id] = {
            "user1": user1,
            "user2": str(user2),
            "logs": [{"user": user1, "timestamp": time.time(), "message": "Chat started"}]
        }

        save_json(DB_PATH_LOGS, logs_db)
        return jsonify({"message": "Chat created", "chat_id": new_chat_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_logs_bp.route("/request-swap/<int:product_id>/<int:user2>", methods=["POST"])
@jwt_required()
def request_swap(product_id, user2):
    """Create a new chat (if not exists) and send a swap request message."""
    try:
        user1 = str(get_jwt_identity().get("id"))
        logs_db = load_json(DB_PATH_LOGS)

        chat_key = next((key for key, log in logs_db.items() if {str(log["user1"]), str(log["user2"])} == {user1, str(user2)}), None)

        if chat_key:
            logs_db[chat_key]["logs"].append({
                "user": user1,
                "timestamp": time.time(),
                "message": f"🔄 Swap request for product {product_id}."
            })
        else:
            chat_key = str(len(logs_db) + 1)
            logs_db[chat_key] = {
                "user1": user1,
                "user2": str(user2),
                "logs": [
                    {"user": user1, "timestamp": time.time(), "message": "Chat started"},
                    {"user": user1, "timestamp": time.time(), "message": f"🔄 Swap request for product {product_id}."}
                ],
            }

        save_json(DB_PATH_LOGS, logs_db)
        return jsonify({"message": "Swap request sent!", "chat_id": chat_key}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500