import os
import shelve

DB_FOLDER = os.path.join(os.path.dirname(__file__), "db")
DB_PATH_TAGS = os.path.join(DB_FOLDER, "tags")

with shelve.open(DB_PATH_TAGS, writeback=True) as tags_db:
    if "valid_tags" in tags_db:
        valid_tags_data = tags_db["valid_tags"]
        tag_names = valid_tags_data["name"]
        default_description = valid_tags_data["description"]

        # Delete the old entry
        del tags_db["valid_tags"]

        # Create individual tag entries
        for idx, tag_name in enumerate(tag_names, start=1):
            tags_db[str(idx)] = {
                "id": str(idx),
                "name": tag_name,
                "description": default_description,
            }

print("Tags migrated successfully!")