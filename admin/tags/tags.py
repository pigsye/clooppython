import os
import json
from flask import Blueprint, jsonify, request

# Blueprint for tags
admin_tags_bp = Blueprint("tags", __name__)

# Path to the tags JSON database
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_TAGS = os.path.join(DB_FOLDER, "tags.json")

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

@admin_tags_bp.route('/tags', methods=['GET'])
def get_all_tags():
    """
    Retrieve all tags with their names and descriptions.
    """
    try:
        tags_db = load_json(DB_PATH_TAGS)
        tags = list(tags_db.values())  # Convert to a list
        return jsonify(tags), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_tags_bp.route('/tags/create', methods=['POST'])
def create_tag():
    """
    Create a new tag in the tags.json file.
    """
    try:
        data = request.json
        tag_name = data.get("name")
        description = data.get("description", "")

        if not tag_name or not tag_name.strip():
            return jsonify({"error": "Tag name cannot be empty"}), 400

        tags_db = load_json(DB_PATH_TAGS)

        # Check for duplicates
        if any(tag["name"] == tag_name for tag in tags_db.values()):
            return jsonify({"error": "Tag already exists"}), 400

        # Generate a unique ID
        tag_id = str(max([int(k) for k in tags_db.keys()] or [0]) + 1)

        # Add the new tag
        new_tag = {"id": tag_id, "name": tag_name, "description": description}
        tags_db[tag_id] = new_tag
        save_json(DB_PATH_TAGS, tags_db)

        return jsonify({"message": f"Tag '{tag_name}' created successfully!", "tag": new_tag}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_tags_bp.route('/tags/delete', methods=['POST'])
def delete_tag():
    """
    Delete a tag from the tags.json file.
    """
    try:
        data = request.json
        tag_name = data.get("name")

        if not tag_name:
            return jsonify({"error": "Tag name is required"}), 400

        tags_db = load_json(DB_PATH_TAGS)

        # Find and delete the tag by name
        for key, value in list(tags_db.items()):
            if value.get("name") == tag_name:
                del tags_db[key]
                save_json(DB_PATH_TAGS, tags_db)
                return jsonify({"message": f"Tag '{tag_name}' deleted successfully!"}), 200

        return jsonify({"error": f"Tag '{tag_name}' not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_tags_bp.route('/tags/update', methods=['POST'])
def update_tag():
    """
    Update an existing tag's name or description.
    """
    try:
        data = request.json
        tag_id = str(data.get("id"))
        new_name = data.get("name")
        new_description = data.get("description")

        if not tag_id:
            return jsonify({"error": "Tag ID is required"}), 400

        tags_db = load_json(DB_PATH_TAGS)

        if tag_id not in tags_db:
            return jsonify({"error": "Tag not found"}), 404

        # Update fields if provided
        if new_name:
            tags_db[tag_id]["name"] = new_name
        if new_description:
            tags_db[tag_id]["description"] = new_description

        save_json(DB_PATH_TAGS, tags_db)

        return jsonify({"message": "Tag updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500