import os
import json
from flask import Blueprint, request, jsonify, send_from_directory

admin_profile_bp = Blueprint("profile", __name__)

# Define paths
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH = os.path.join(DB_FOLDER, "accounts.json")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../../api/uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_json():
    """Load accounts JSON file."""
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(data):
    """Save data to accounts JSON file."""
    with open(DB_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def allowed_file(filename):
    """Check allowed file extensions."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_profile_bp.route("/changeprofile/<int:user_id>", methods=["POST"])
def change_profile_picture(user_id):
    """Upload and update the user's profile picture."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    file_extension = file.filename.rsplit(".", 1)[1].lower()
    new_filename = f"pfp{user_id}.{file_extension}"
    filepath = os.path.join(UPLOAD_FOLDER, new_filename)

    try:
        accounts_db = load_json()

        if str(user_id) not in accounts_db:
            return jsonify({"error": "User not found"}), 404

        # Delete old profile picture
        current_pfp = accounts_db[str(user_id)].get("pfp", None)
        if current_pfp and current_pfp.startswith("/uploads/"):
            old_filepath = os.path.join(UPLOAD_FOLDER, os.path.basename(current_pfp))
            if os.path.exists(old_filepath):
                os.remove(old_filepath)

        # Save new profile picture
        file.save(filepath)
        accounts_db[str(user_id)]["pfp"] = f"/uploads/{new_filename}"
        save_json(accounts_db)

        return jsonify({"message": "Profile picture updated successfully!", "url": f"/uploads/{new_filename}"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@admin_profile_bp.route("/uploads/<filename>")
def serve_uploaded_file(filename):
    """Serve uploaded profile pictures."""
    return send_from_directory(UPLOAD_FOLDER, filename)

@admin_profile_bp.route("/deleteaccount/<int:user_id>", methods=["POST"])
def delete_account(user_id):
    """Delete an account from the database."""
    try:
        accounts_db = load_json()
        if str(user_id) not in accounts_db:
            return jsonify({"error": "User not found"}), 404

        # Remove profile picture
        pfp = accounts_db[str(user_id)].get("pfp", None)
        if pfp and pfp.startswith("/uploads/"):
            os.remove(os.path.join(UPLOAD_FOLDER, os.path.basename(pfp)))

        # Delete user
        del accounts_db[str(user_id)]
        save_json(accounts_db)

        return jsonify({"message": "Account deleted successfully."}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500