import os
import json
from flask import Blueprint, jsonify

admin_accounts_bp = Blueprint("accounts", __name__)

# ✅ Define the path to the JSON database file
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH = os.path.join(DB_FOLDER, "accounts.json")  # Path to `accounts.json`
DEFAULT_PFP_URL = "/account.svg"

def load_json(db_path):
    """Load JSON file and return a dictionary."""
    if not os.path.exists(db_path):
        return {}  # Return an empty dictionary if the file doesn't exist
    with open(db_path, "r", encoding="utf-8") as file:
        return json.load(file)

@admin_accounts_bp.route("/account", methods=["GET"])
def get_accounts():
    """Fetch all accounts without sensitive data."""
    accounts_db = load_json(DB_PATH)

    accounts = []
    for account in accounts_db.values():
        sanitized_account = {
            "id": account.get("id"),
            "username": account.get("username"),
            "email": account.get("email"),
            "pfp": account.get("pfp", DEFAULT_PFP_URL),
        }
        accounts.append(sanitized_account)

    # ✅ Sort accounts by `id` numerically
    sorted_accounts = sorted(accounts, key=lambda x: int(x["id"]))

    return jsonify(sorted_accounts)