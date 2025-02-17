from flask import Blueprint, jsonify, request
import os
import shelve
from werkzeug.utils import secure_filename
from PIL import Image

user_submissions_bp = Blueprint("user_submissions", __name__)

# Database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_SUBMISSIONS = os.path.join(DB_FOLDER, "submissions")

# Upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../api/uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if uploaded file is an allowed image format."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image(image_path):
    """Resize and compress image before saving."""
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")  # Ensure compatibility

            # Resize if width > 1080px while keeping aspect ratio
            max_width = 1080
            if img.width > max_width:
                aspect_ratio = img.height / img.width
                new_height = int(max_width * aspect_ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)

            # Save with optimized quality
            img.save(image_path, "JPEG", quality=85, optimize=True)
    except Exception as e:
        print(f"❌ Error compressing image: {e}")

@user_submissions_bp.route("/submit", methods=["POST"])
def submit_item():
    """
    Handle item submission with file uploads and image compression.
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
                filepath = os.path.join(UPLOAD_FOLDER, filename)

                file.save(filepath)  # Save original file
                compress_image(filepath)  # Compress the image

                filenames.append(filename)

        # Store submission in shelve database
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