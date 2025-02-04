import os
import shelve
from flask import Blueprint, request, jsonify, send_from_directory

admin_profile_bp = Blueprint('profile', __name__)

# Define paths
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH = os.path.join(DB_FOLDER, "accounts")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../../uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Utility function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_profile_bp.route('/changeprofile/<int:user_id>', methods=['POST'])
def change_profile_picture(user_id):
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Only PNG, JPG, JPEG, and GIF are allowed."}), 400

    # Extract the file extension
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    new_filename = f"pfp{user_id}.{file_extension}"
    filepath = os.path.join(UPLOAD_FOLDER, new_filename)

    try:
        # Check for and delete the old profile picture
        with shelve.open(DB_PATH, writeback=True) as db:
            user_key = str(user_id)
            if user_key not in db:
                return jsonify({"error": "User not found"}), 404

            # Get current profile picture URL if exists
            current_pfp = db[user_key].get("pfp", None)
            if current_pfp and current_pfp.startswith("/uploads/"):
                old_filepath = os.path.join(UPLOAD_FOLDER, os.path.basename(current_pfp))
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)

            # Save the new profile picture path in the database
            db[user_key]['pfp'] = f"/uploads/{new_filename}"
            db.sync()

        # Save the new file
        file.save(filepath)

        return jsonify({
            "message": "Profile picture updated successfully!",
            "url": f"/uploads/{new_filename}"
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Route to serve uploaded files
@admin_profile_bp.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@admin_profile_bp.route('/deleteaccount/<int:user_id>', methods=['POST'])
def delete_account(user_id):
    try:
        with shelve.open(DB_PATH, writeback=True) as db:
            user_key = str(user_id)

            # Check if the user exists
            if user_key not in db:
                return jsonify({"error": "User not found"}), 404

            # Delete profile picture if it exists
            current_pfp = db[user_key].get("pfp", None)
            if current_pfp and current_pfp.startswith("/uploads/"):
                old_filepath = os.path.join(UPLOAD_FOLDER, os.path.basename(current_pfp))
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)

            # Remove the user from the database
            del db[user_key]
            db.sync()

        return jsonify({"message": "Account deleted successfully."}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
