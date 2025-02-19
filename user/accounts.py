import os
import json
import datetime
import uuid
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from PIL import Image

user_accounts_bp = Blueprint("user_accounts", __name__)
bcrypt = Bcrypt()

# Database path (fixed to ../db)
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts.json")

# Upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../api/uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

@user_accounts_bp.route("/auth/register", methods=['POST'])
def create_account():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    accounts = load_json(DB_PATH_ACCOUNTS)

    for account in accounts.values():
        if account["email"] == email:
            return jsonify({"error": "Email already in use"}), 400

    account_id = str(len(accounts) + 1)

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_account = {
        "id": account_id,
        "username": name.strip(),
        "email": email.strip(),
        "password": hashed_password,
        "role": "user",
        "status": "active",
        "failed_attempts": 0,
        "disabled": False,
        "disabled_until": None,
    }

    accounts[account_id] = new_account
    save_json(DB_PATH_ACCOUNTS, accounts)

    return jsonify({"message": "Account created successfully!"}), 201

@user_accounts_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    accounts = load_json(DB_PATH_ACCOUNTS)

    user = next((user for user in accounts.values() if user["email"] == email), None)

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity={"id": user["id"], "role": "user"}, expires_delta=datetime.timedelta(hours=24))

    return jsonify({"token": token}), 200

@user_accounts_bp.route("/profile/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_profile(user_id):
    """Fetch user profile data securely."""
    user_id = str(user_id)
    user_identity = get_jwt_identity()

    accounts = load_json(DB_PATH_ACCOUNTS)

    if user_id not in accounts:
        return jsonify({"error": f"User {user_id} not found."}), 404

    user_data = accounts[user_id]
    user_data.pop("password", None)

    return jsonify({"profile": user_data}), 200

@user_accounts_bp.route("/profile/<int:user_id>/upload", methods=["POST"])
def upload_profile_picture(user_id):
    """Upload and compress a profile picture before saving."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(f"user_{user_id}.jpg")
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        image = Image.open(file)
        image = image.convert("RGB")

        max_width = 800
        if image.width > max_width:
            height = int((max_width / image.width) * image.height)
            image = image.resize((max_width, height), Image.LANCZOS)

        image.save(filepath, format="JPEG", quality=85, optimize=True)

        accounts = load_json(DB_PATH_ACCOUNTS)
        user_id = str(user_id)

        if user_id not in accounts:
            return jsonify({"error": "User not found"}), 404

        accounts[user_id]["pfp"] = filename
        save_json(DB_PATH_ACCOUNTS, accounts)

        return jsonify({"message": "Profile picture updated successfully!", "filename": filename}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@user_accounts_bp.route("/profile/<int:user_id>", methods=["POST"])
def update_user_profile(user_id):
    """Update user profile data."""
    data = request.json
    user_id = str(user_id)

    accounts = load_json(DB_PATH_ACCOUNTS)

    if user_id not in accounts:
        return jsonify({"error": "User not found"}), 404

    user_data = accounts[user_id]

    if "username" in data:
        user_data["username"] = data["username"].strip()
    if "email" in data:
        user_data["email"] = data["email"].strip()
    if "phone" in data:
        user_data["phone"] = data["phone"].strip()
    if "bio" in data:
        user_data["bio"] = data["bio"].strip()

    accounts[user_id] = user_data
    save_json(DB_PATH_ACCOUNTS, accounts)

    return jsonify({"message": "Profile updated successfully!"}), 200

@user_accounts_bp.route("/auth/verify/<token>", methods=["GET"])
def verify_email(token):
    """Verify user email using a token."""
    accounts = load_json(DB_PATH_ACCOUNTS)

    for user_id, user in accounts.items():
        if user.get("verification_token") == token:
            user["status"] = "active"
            user["verification_token"] = None
            accounts[user_id] = user
            save_json(DB_PATH_ACCOUNTS, accounts)
            return jsonify({"message": "Account verified successfully!"}), 200

    return jsonify({"error": "Invalid or expired verification link."}), 400

@user_accounts_bp.route("/profile/<int:user_id>/change-password", methods=["POST"])
@jwt_required()
def change_password(user_id):
    """Allow users to change their password securely."""
    data = request.json
    current_password = data.get("currentPassword")
    new_password = data.get("newPassword")

    if not current_password or not new_password or len(new_password) < 8:
        return jsonify({"error": "Invalid input"}), 400

    user_identity = get_jwt_identity()
    if str(user_identity["id"]) != str(user_id):
        return jsonify({"error": "Unauthorized action."}), 403

    accounts = load_json(DB_PATH_ACCOUNTS)

    if str(user_id) not in accounts:
        return jsonify({"error": "User not found"}), 404

    user = accounts[str(user_id)]

    if not bcrypt.check_password_hash(user["password"], current_password):
        return jsonify({"error": "Incorrect current password."}), 401

    user["password"] = bcrypt.generate_password_hash(new_password).decode("utf-8")
    accounts[str(user_id)] = user
    save_json(DB_PATH_ACCOUNTS, accounts)

    return jsonify({"message": "Password updated successfully!"}), 200