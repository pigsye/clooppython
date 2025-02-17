from flask import Blueprint, request, jsonify
import os
import shelve
import time
from flask_jwt_extended import jwt_required, get_jwt_identity

user_logs_bp = Blueprint("user_logs", __name__)

# Database paths
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_LOGS = os.path.join(DB_FOLDER, "logs")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts")

def get_username(user_id):
    """Fetch username from accounts database."""
    try:
        with shelve.open(DB_PATH_ACCOUNTS) as db:
            user_data = db.get(str(user_id), {})
            return user_data.get("username", f"User {user_id}")
    except Exception:
        return f"User {user_id}"  # Fallback if error occurs

@user_logs_bp.route("/chats", methods=["GET"])
@jwt_required()  # Ensure user is logged in
def get_chats():
    """Fetch all chats for the logged-in user."""
    try:
        user_id = str(get_jwt_identity().get("id"))  # Extract user ID from JWT
        user_chats = {}

        with shelve.open(DB_PATH_LOGS) as db:
            for key, log in db.items():
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

        if request.method == "GET":
            # ✅ Handle fetching messages
            with shelve.open(DB_PATH_LOGS) as db:
                chat_key = None
                for key, log in db.items():
                    if {str(log["user1"]), str(log["user2"])} == {user1, str(user2)}:
                        chat_key = key
                        break

                if not chat_key:
                    return jsonify({"logs": []}), 200  # No messages found

                logs = db[chat_key]["logs"]
                logs.sort(key=lambda x: x["timestamp"])
                return jsonify({"logs": logs}), 200

        elif request.method == "POST":
            # ✅ Handle sending messages
            data = request.json
            message = data.get("message", "").strip()

            if not message:
                return jsonify({"error": "Message is required"}), 400

            with shelve.open(DB_PATH_LOGS, writeback=True) as db:
                chat_key = None
                for key, log in db.items():
                    if {str(log["user1"]), str(log["user2"])} == {user1, str(user2)}:
                        chat_key = key
                        break

                new_message = {
                    "user": user1,
                    "timestamp": time.time(),
                    "message": message
                }

                if chat_key:
                    db[chat_key]["logs"].append(new_message)
                else:
                    chat_key = str(len(db) + 1)
                    db[chat_key] = {"user1": user1, "user2": str(user2), "logs": [new_message]}

                return jsonify({"message": "Message sent successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_logs_bp.route("/start-chat/<int:user2>", methods=["POST"])
@jwt_required()
def start_chat(user2):
    """Create a new chat between logged-in user and another user."""
    try:
        user1 = str(get_jwt_identity().get("id"))

        with shelve.open(DB_PATH_LOGS, writeback=True) as db:
            for chat_id, chat in db.items():
                if {str(chat["user1"]), str(chat["user2"])} == {user1, str(user2)}:
                    return jsonify({"message": "Chat already exists", "chat_id": chat_id}), 200

            new_chat_id = str(len(db) + 1)
            db[new_chat_id] = {
                "user1": user1,
                "user2": str(user2),
                "logs": [{"user": user1, "timestamp": time.time(), "message": "Chat started"}]
            }

        return jsonify({"message": "Chat created", "chat_id": new_chat_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@user_logs_bp.route("/request-swap/<int:product_id>/<int:user2>", methods=["POST"])
@jwt_required()
def request_swap(product_id, user2):
    """Create a new chat (if not exists) and send a swap request message."""
    try:
        user1 = str(get_jwt_identity().get("id"))  # Get logged-in user ID

        with shelve.open(DB_PATH_LOGS, writeback=True) as db:
            chat_id = None

            # Check if a chat already exists
            for key, log in db.items():
                if {str(log["user1"]), str(log["user2"])} == {user1, str(user2)}:
                    chat_id = key
                    break

            if chat_id:
                # Chat exists → Add swap request message
                db[chat_id]["logs"].append({
                    "user": user1,
                    "timestamp": time.time(),
                    "message": f"🔄 Swap request for product {product_id}."
                })
            else:
                # No chat exists → Create new chat with swap request
                chat_id = str(len(db) + 1)
                db[chat_id] = {
                    "user1": user1,
                    "user2": str(user2),
                    "logs": [
                        {"user": user1, "timestamp": time.time(), "message": "Chat started"},
                        {"user": user1, "timestamp": time.time(), "message": f"🔄 Swap request for product {product_id}."}
                    ],
                }

        return jsonify({"message": "Swap request sent!", "chat_id": chat_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500