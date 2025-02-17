import os
import shelve
from flask import Blueprint, jsonify, request

# Blueprint for tags
admin_tags_bp = Blueprint("tags", __name__)

# Path to the tags database
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_TAGS = os.path.join(DB_FOLDER, "tags")


@admin_tags_bp.route('/tags', methods=['GET'])
def get_all_tags():
    """
    Retrieve all tags with their names and descriptions.
    """
    try:
        with shelve.open(DB_PATH_TAGS) as tags_db:
            tags = list(tags_db.values())  # Each tag is now a dictionary
        print(tags)
        return jsonify(tags), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_tags_bp.route('/create', methods=['POST'])
def create_tag():
    try:
        data = request.json
        print("Received data:", data)  # Debugging received data

        tag_name = data.get("name")
        description = data.get("description", "")

        if not tag_name or not tag_name.strip():
            return jsonify({"error": "Tag name cannot be empty"}), 400

        # Open the shelve database within the context manager
        with shelve.open(DB_PATH_TAGS, writeback=True) as tags_db:
            print("Current tags in DB:", list(tags_db.values()))  # Debugging database content

            # Check for duplicates
            if any(tag["name"] == tag_name for tag in tags_db.values()):
                print(f"Tag '{tag_name}' already exists.")
                return jsonify({"error": "Tag already exists"}), 400

            # Generate a unique ID
            tag_id = str(max([int(k) for k in tags_db.keys()] + [0]) + 1)

            # Add the new tag
            new_tag = {"id": tag_id, "name": tag_name, "description": description}
            tags_db[tag_id] = new_tag  # Save in the database

            print(f"Tag '{tag_name}' added successfully with ID {tag_id}.")  # Debugging success

            # Return the response while the shelf is still open
            return jsonify({"message": f"Tag '{tag_name}' created successfully!", "tag": new_tag}), 200

    except Exception as e:
        print(f"ERROR: {e}")  # Log unexpected errors
        return jsonify({"error": str(e)}), 500


@admin_tags_bp.route('/delete', methods=['POST'])
def delete_tag():
    """
    Delete a tag from the tags.db
    """
    try:
        data = request.json
        tag_name = data.get("name")

        if not tag_name:
            return jsonify({"error": "Tag name is required"}), 400

        with shelve.open(DB_PATH_TAGS, writeback=True) as tags_db:
            # Find and delete the tag by name
            for key, value in list(tags_db.items()):
                if value.get("name") == tag_name:  # Compare the "name" field in the tag object
                    del tags_db[key]
                    return jsonify({"message": f"Tag '{tag_name}' deleted successfully!"}), 200

        return jsonify({"error": f"Tag '{tag_name}' not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_tags_bp.route('/update', methods=['POST'])
def update_tag():
    try:
        data = request.json
        tag_id = data.get("id")
        new_name = data.get("name")
        new_description = data.get("description")

        if not tag_id:
            return jsonify({"error": "Tag ID is required"}), 400

        with shelve.open(DB_PATH_TAGS, writeback=True) as tags_db:
            if tag_id not in tags_db:
                return jsonify({"error": "Tag not found"}), 404

            tag = tags_db[tag_id]
            if new_name:
                tag["name"] = new_name
            if new_description:
                tag["description"] = new_description

            tags_db[tag_id] = tag

        return jsonify({"message": "Tag updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500