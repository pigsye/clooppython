from flask import Blueprint, jsonify
import os
import json

user_tags_bp = Blueprint("user_tags", __name__)

# Database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_TAGS = os.path.join(DB_FOLDER, "tags.json")

def load_json(db_path):
    """Load JSON data from a file."""
    if not os.path.exists(db_path):
        return {}
    with open(db_path, "r", encoding="utf-8") as file:
        return json.load(file)

@user_tags_bp.route("/tags", methods=["GET"])
def get_tags():
    """
    Fetch all available tags from the JSON database.
    """
    try:
        tags_db = load_json(DB_PATH_TAGS)

        # Sort tags numerically by their ID
        sorted_tags = sorted(tags_db.values(), key=lambda x: int(x["id"]))

        return jsonify({"tags": sorted_tags}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500