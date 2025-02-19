import shelve
import os
import json
import glob

# ✅ List of database names (without extensions)
DB_FOLDER = "db"  # Make sure this is the correct path
db_files = ["tags", "products", "accounts", "submissions", "logs", "feedback", "orders", "ratings", "reports", "wishlist"]

def convert_shelve_to_json(db_name):
    """Read a shelve database and write its contents to a JSON file."""
    db_path = os.path.join(DB_FOLDER, db_name)
    json_path = os.path.join(DB_FOLDER, f"{db_name}.json")

    try:
        # ✅ Open the database
        with shelve.open(db_path, flag="r") as db:
            data = dict(db)  # Convert to dictionary

        # ✅ Save to JSON file
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

        print(f"✅ Converted {db_name} → {json_path}")

    except Exception as e:
        print(f"❌ ERROR converting {db_name}: {e}")

# 🔍 Iterate through all DB files
for db_file in db_files:
    possible_db_files = glob.glob(os.path.join(DB_FOLDER, db_file) + ".*")  # Find Shelve files

    if possible_db_files:
        convert_shelve_to_json(db_file)  # Convert only if the file exists
    else:
        print(f"⚠️  {db_file} does not exist in {DB_FOLDER}.")

print("\n🎯 **Database Conversion Complete!** You can now delete the .db files if everything looks good.")