from flask import Blueprint, jsonify, request
import os
import shelve
from werkzeug.utils import secure_filename

user_accounts_bp = Blueprint("user_accounts", __name__)

# Database path (fixed to ../db)
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts")

# Upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@user_accounts_bp.route("/profile/<int:user_id>", methods=["GET"])
def get_user_profile(user_id):
    """
    Fetch user profile data, excluding password, and include profile picture filename.
    """
    try:
        with shelve.open(DB_PATH_ACCOUNTS) as db:
            user_data = db.get(str(user_id))

        if not user_data:
            return jsonify({"error": "User not found"}), 404

        # Remove password before sending data
        user_data.pop("password", None)

        return jsonify({"profile": user_data}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@user_accounts_bp.route("/profile/<int:user_id>/upload", methods=["POST"])
def upload_profile_picture(user_id):
    """
    Upload a profile picture and update the user's profile with the new image filename.
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(f"user_{user_id}_{file.filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)  # Save the uploaded file

            with shelve.open(DB_PATH_ACCOUNTS, writeback=True) as db:
                if str(user_id) not in db:
                    return jsonify({"error": "User not found"}), 404

                db[str(user_id)]["pfp"] = filename  # Store filename in database

            return jsonify({"message": "Profile picture updated successfully!", "filename": filename}), 200

        return jsonify({"error": "Invalid file type"}), 400

    except Exception as e:
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
