from flask import Blueprint, jsonify
import os
import shelve

user_tags_bp = Blueprint("user_tags", __name__)

# Database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_TAGS = os.path.join(DB_FOLDER, "tags")

@user_tags_bp.route("/tags", methods=["GET"])
def get_tags():
    """
    Fetch all available tags from the database.
    """
    try:
        with shelve.open(DB_PATH_TAGS) as db:
            # Sort keys numerically and retrieve tags
            tags = [db[key] for key in sorted(db.keys(), key=int)]

        return jsonify({"tags": tags}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500