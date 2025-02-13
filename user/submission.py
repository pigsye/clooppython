from flask import Blueprint, jsonify, request
import os
import shelve
from werkzeug.utils import secure_filename

user_submissions_bp = Blueprint("user_submissions", __name__)

# Database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_SUBMISSIONS = os.path.join(DB_FOLDER, "submissions")

# Upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@user_submissions_bp.route("/submit", methods=["POST"])
def submit_item():
    """
    Handle item submission with file uploads.
    """
    try:
        data = request.form.to_dict()
        files = request.files.getlist("photos")

        if not data.get("title") or len(data["title"]) < 3:
            return jsonify({"error": "Title must be at least 3 characters."}), 400

        if not data.get("selectedTags"):
            return jsonify({"error": "At least one tag is required."}), 400

        if not files:
            return jsonify({"error": "At least one photo is required."}), 400

        filenames = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                filenames.append(filename)

        with shelve.open(DB_PATH_SUBMISSIONS, writeback=True) as db:
            new_id = str(len(db) + 1)  # Generate new ID
            db[new_id] = {
                "clothing_name": data["title"],
                "description": data.get("description", ""),
                "customerId": "1",  # Assuming user ID 1 for now
                "tags": data["selectedTags"].split(","),
                "images": filenames,
            }

        return jsonify({"message": "Submission successful!"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500