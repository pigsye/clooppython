from flask import Blueprint, jsonify, request
import os
import shelve
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime
from flask import make_response
from werkzeug.security import check_password_hash
import uuid
from flask_mail import Message
from PIL import Image

user_accounts_bp = Blueprint("user_accounts", __name__)
bcrypt = Bcrypt()

# Database path (fixed to ../db)
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts")

# Upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../api/uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user(email):
    """Retrieve a user by email from the database."""
    with shelve.open(DB_PATH_ACCOUNTS) as db:
        for user_id, user in db.items():
            if user.get("email") == email:
                return user_id, user  # Return both user ID and user data
    return None, None

@user_accounts_bp.route("/profile/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_profile(user_id):
    """Fetch user profile data securely."""
    try:
        user_id = str(user_id)  # ✅ Ensure key is a string

        # 🔍 Debugging: Print the token identity
        user_identity = get_jwt_identity()
        print(f"✅ Authenticated User: {user_identity}")

        with shelve.open(DB_PATH_ACCOUNTS) as db:
            if user_id not in db:
                print(f"❌ User {user_id} not found in database.")
                return jsonify({"error": f"User {user_id} not found."}), 404

            user_data = db[user_id]

        user_data.pop("password", None)  # ✅ Remove password for security

        return jsonify({"profile": user_data}), 200

    except Exception as e:
        print(f"❌ Error in /profile/{user_id}: {str(e)}")  # Debugging Log
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

from PIL import Image

@user_accounts_bp.route("/profile/<int:user_id>/upload", methods=["POST"])
def upload_profile_picture(user_id):
    """
    Upload and compress a profile picture before saving.
    """
    try:
        if "file" not in request.files:
            print("❌ No file found in request.")  # Debugging log
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]

        if file.filename == "":
            print("❌ No selected file.")  # Debugging log
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(f"user_{user_id}.jpg")  # ✅ Always save as JPG
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            # Ensure upload directory exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            # ✅ Open image using PIL
            try:
                image = Image.open(file)
                image = image.convert("RGB")  # Convert to RGB to prevent format errors

                # ✅ Resize (Maintain Aspect Ratio, Max Width: 800px)
                max_width = 800
                if image.width > max_width:
                    height = int((max_width / image.width) * image.height)
                    image = image.resize((max_width, height), Image.LANCZOS)  # ✅ Use LANCZOS for Pillow v10+

                # ✅ Save with Compression
                image.save(filepath, format="JPEG", quality=85, optimize=True)
            except Exception as img_err:
                print(f"❌ Error processing image: {img_err}")  # Debugging log
                return jsonify({"error": "Invalid image file."}), 400

            # ✅ Update Database Entry
            with shelve.open(DB_PATH_ACCOUNTS, writeback=True) as db:
                user_key = str(user_id)  # ✅ Ensure key is string

                if user_key not in db:
                    print(f"❌ User {user_id} not found in database.")
                    return jsonify({"error": "User not found"}), 404

                db[user_key]["pfp"] = filename

            print(f"✅ Profile picture saved: {filename}")  # Debugging log
            return jsonify({"message": "Profile picture updated successfully!", "filename": filename}), 200

        print("❌ Invalid file type.")  # Debugging log
        return jsonify({"error": "Invalid file type"}), 400

    except Exception as e:
        print(f"❌ Unexpected error: {e}")  # Debugging log
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@user_accounts_bp.route("/profile/<int:user_id>", methods=["POST"])
def update_user_profile(user_id):
    """
    Update user profile data.
    """
    try:
        data = request.json
        with shelve.open(DB_PATH_ACCOUNTS, writeback=True) as db:
            if str(user_id) not in db:
                return jsonify({"error": "User not found"}), 404

            user_data = db[str(user_id)]

            # Update fields if provided
            if "username" in data:
                user_data["username"] = data["username"].strip()
            if "email" in data:
                user_data["email"] = data["email"].strip()
            if "phone" in data:
                user_data["phone"] = data["phone"].strip()  # Add phone if missing
            if "bio" in data:
                user_data["bio"] = data["bio"].strip()  # Add bio if missing

            db[str(user_id)] = user_data  # Save changes

        return jsonify({"message": "Profile updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
@user_accounts_bp.route("/user/<int:user_id>", methods=["GET"])
def get_public_user_profile(user_id):
    """
    Fetch a public user profile by ID, excluding sensitive information like passwords.
    """
    try:
        with shelve.open(DB_PATH_ACCOUNTS) as db:
            user_data = db.get(str(user_id))

        if not user_data:
            return jsonify({"error": "User not found"}), 404

        # Remove sensitive information
        user_data.pop("password", None)

        return jsonify({"profile": user_data}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@user_accounts_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    with shelve.open(DB_PATH_ACCOUNTS, writeback=True) as db:
        user_id = None
        user = None

        # 🔍 Find user by email
        for uid, user_data in db.items():
            if user_data.get("email") == email:
                user_id = uid
                user = user_data
                break

        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        # 🔍 Check if the account is locked
        failed_attempts = user.get("failed_attempts", 0)
        disabled_until = user.get("disabled_until")

        if disabled_until:
            current_time = datetime.datetime.now().timestamp()
            if current_time < disabled_until:
                remaining_time = int((disabled_until - current_time) / 60)
                return jsonify({"error": f"Account locked. Try again in {remaining_time} minutes."}), 403

        # 🔐 Verify password
        if not bcrypt.check_password_hash(user["password"], password):
            user["failed_attempts"] = failed_attempts + 1

            # 🔒 Lock account if attempts exceed 5
            if user["failed_attempts"] >= 5:
                user["disabled_until"] = datetime.datetime.now().timestamp() + 900  # Lock for 15 minutes (900s)
                db[user_id] = user  # ✅ Ensure changes persist in shelve
                return jsonify({"error": "Account locked due to multiple failed attempts. Try again later."}), 403

            db[user_id] = user  # ✅ Save changes to failed_attempts
            return jsonify({"error": f"Invalid credentials. {5 - user['failed_attempts']} attempts remaining."}), 401

        # ✅ Reset failed attempts on successful login
        user["failed_attempts"] = 0
        user["disabled_until"] = None
        db[user_id] = user  # ✅ Save reset values in the database

        # 🔑 Generate JWT Token
        token = create_access_token(
            identity={"id": user_id, "role": "user"},
            fresh=True,
            expires_delta=datetime.timedelta(hours=24)
        )

        return jsonify({"token": token}), 200

# Protected Route to Verify User ID (Optional)
@user_accounts_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Fetch the logged-in user's details and check if they are disabled."""
    try:
        user_id = str(get_jwt_identity()["id"])

        with shelve.open(DB_PATH_ACCOUNTS) as db:
            user = db.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # 🔍 Check if user is disabled
        if user.get("disabled", False):
            return jsonify({"error": "Account disabled", "disabled": True}), 403

        return jsonify({
            "username": user.get("username", ""),
            "id": user_id,
            "role": user.get("role", "user"),
            "disabled": False  # ✅ Explicitly set to false for clarity
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@user_accounts_bp.route("/auth/register", methods=['POST'])
def create_account():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    with shelve.open(DB_PATH_ACCOUNTS, writeback=True) as db:
        for user in db.values():
            if user.get("email") == email:
                return jsonify({"error": "Email already in use"}), 400

        account_id = str(len(db) + 1)

        # ✅ Ensure password is hashed properly
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_account = {
            "id": account_id,
            "username": name.strip(),
            "email": email.strip(),
            "password": hashed_password,  # ✅ Securely hashed password
            "role": "user",
            "status": "active",
            "failed_attempts": 0,
            "disabled": False,
            "disabled_until": None,
        }

        db[account_id] = new_account

    return jsonify({"message": "Account created successfully!"}), 201

@user_accounts_bp.route("/profile/<int:user_id>/change-password", methods=["POST"])
@jwt_required()
def change_password(user_id):
    """Allow users to change their password securely."""
    try:
        data = request.json
        current_password = data.get("currentPassword")
        new_password = data.get("newPassword")

        if not current_password or not new_password:
            return jsonify({"error": "All fields are required."}), 400

        if len(new_password) < 8:
            return jsonify({"error": "New password must be at least 8 characters long."}), 400

        user_identity = get_jwt_identity()
        if str(user_identity["id"]) != str(user_id):
            return jsonify({"error": "Unauthorized action."}), 403

        with shelve.open(DB_PATH_ACCOUNTS, writeback=True) as db:
            if str(user_id) not in db:
                return jsonify({"error": "User not found."}), 404

            user = db[str(user_id)]

            # 🔒 Verify current password
            if not bcrypt.checkpw(current_password.encode(), user["password"].encode()):
                return jsonify({"error": "Incorrect current password."}), 401

            # 🔐 Hash new password
            hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

            # ✅ Update password in database
            user["password"] = hashed_password
            db[str(user_id)] = user  # Save changes

        return jsonify({"message": "Password updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@user_accounts_bp.route("/auth/verify/<token>", methods=["GET"])
def verify_email(token):
    with shelve.open(DB_PATH_ACCOUNTS, writeback=True) as db:
        for user_id, user in db.items():
            if user.get("verification_token") == token:
                user["status"] = "active"  # ✅ Mark user as verified
                user["verification_token"] = None  # Remove the token
                db[user_id] = user
                return jsonify({"message": "Account verified successfully!"}), 200

    return jsonify({"error": "Invalid or expired verification link."}), 400