from flask import Blueprint, request, jsonify
import os
import shelve
import time

user_logs_bp = Blueprint("user_logs", __name__)

# Database paths (using ../db)
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_LOGS = os.path.join(DB_FOLDER, "logs")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts")

def get_username(user_id):
    """
    Fetch username from accounts database.
    """
    try:
        with shelve.open(DB_PATH_ACCOUNTS) as db:
            user_data = db.get(str(user_id), {})
            return user_data.get("username", f"User {user_id}")
    except Exception as e:
        return f"User {user_id}"  # Fallback if database error occurs

@user_logs_bp.route("/chats/<int:user_id>", methods=["GET"])
def get_chats(user_id):
    """
    Fetch all chats involving a specific user, including usernames.
    """
    try:
        user_id = str(user_id)  # Ensure user ID is string for comparison
        user_chats = {}

        with shelve.open(DB_PATH_LOGS) as db:
            for key, log in db.items():
                if str(log["user1"]) == user_id or str(log["user2"]) == user_id:
                    other_user_id = str(log["user2"]) if str(log["user1"]) == user_id else str(log["user1"])
                    other_username = get_username(other_user_id)  # Fetch username

                    user_chats[other_user_id] = {
                        "user_id": other_user_id,
                        "username": other_username,  # Include username
                        "logs": sorted(log["logs"], key=lambda x: x["timestamp"])
                    }

        return jsonify({"chats": user_chats}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@user_logs_bp.route("/chats/<int:user1>/<int:user2>", methods=["GET", "POST"])
def chat_logs(user1, user2):
    """
    Handle fetching and sending messages in chat.
    """
    try:
        if request.method == "GET":
            # Fetch chat logs
            with shelve.open(DB_PATH_LOGS) as db:
                chat_key = None
                for key, log in db.items():
                    if (log["user1"] == user1 and log["user2"] == user2) or (log["user1"] == user2 and log["user2"] == user1):
                        chat_key = key
                        break

                if not chat_key:
                    return jsonify({"logs": []}), 200  # No messages yet

                logs = db[chat_key]["logs"]
                logs.sort(key=lambda x: x["timestamp"])  # Ensure chronological order

            return jsonify({"logs": logs}), 200

        elif request.method == "POST":
            # Store a new chat message
            data = request.json
            message = data.get("message", "").strip()

            if not message:
                return jsonify({"error": "Message is required"}), 400

            new_message = {
                "user": user1,  # Assume the sender is always user1 for now
                "timestamp": time.time(),
                "message": message
            }

            with shelve.open(DB_PATH_LOGS, writeback=True) as db:
                chat_key = None
                for key, log in db.items():
                    if (log["user1"] == user1 and log["user2"] == user2) or (log["user1"] == user2 and log["user2"] == user1):
                        chat_key = key
                        break

                if chat_key:
                    db[chat_key]["logs"].append(new_message)
                else:
                    chat_key = str(int(time.time()))  # Unique key using timestamp
                    db[chat_key] = {"user1": user1, "user2": user2, "logs": [new_message]}

            return jsonify({"message": "Message sent successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
@user_logs_bp.route("/start-chat/<int:user_id>", methods=["POST"])
def start_chat(user_id):
    """
    Create a new chat log between user 1 (current assumed user) and the specified user.
    """
    try:
        current_user_id = "1"  # Assuming user 1 for now

        with shelve.open(DB_PATH_LOGS, writeback=True) as db:
            # Check if a chat already exists
            for chat_id, chat in db.items():
                if {chat["user1"], chat["user2"]} == {int(current_user_id), user_id}:
                    return jsonify({"message": "Chat already exists", "chat_id": chat_id}), 200

            # Create a new chat entry
            new_chat_id = str(len(db) + 1)  # Generate new chat ID
            db[new_chat_id] = {
                "user1": int(current_user_id),
                "user2": user_id,
                "logs": [{"user": int(current_user_id), "timestamp": time.time(), "message": "Chat started"}],
            }

        return jsonify({"message": "Chat created", "chat_id": new_chat_id}), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
