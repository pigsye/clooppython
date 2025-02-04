import os
import shelve
from flask import Blueprint, jsonify

admin_accounts_bp = Blueprint('accounts', __name__)

# Define the path to the database folder
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH = os.path.join(DB_FOLDER, "accounts")  # Path to the `accounts` database file
DEFAULT_PFP_URL = "/account.svg"

@admin_accounts_bp.route('/', methods=['GET'])
def get_accounts():
    accounts = []
    with shelve.open(DB_PATH) as db:
        for account in db.values():
            sanitized_account = {
                "id": account.get("id"),
                "username": account.get("username"),
                "email": account.get("email"),
                "pfp": account.get("pfp", DEFAULT_PFP_URL)
            }

            accounts.append(sanitized_account)

    # Sort accounts by `id` numerically
    sorted_accounts = sorted(accounts, key=lambda x: int(x["id"]))

    return jsonify(sorted_accounts)