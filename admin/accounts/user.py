import os
import json
from flask import Blueprint, jsonify

admin_user_bp = Blueprint("user", __name__)

# Define the path to the database folder
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")

# Define paths to individual database files
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts.json")
DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products.json")
DB_PATH_WISHLIST = os.path.join(DB_FOLDER, "wishlist.json")
DB_PATH_RATINGS = os.path.join(DB_FOLDER, "ratings.json")

DEFAULT_PFP_URL = "/account.svg"

def load_json(db_path):
    """Load JSON data from file."""
    if not os.path.exists(db_path):
        return {}
    with open(db_path, "r", encoding="utf-8") as file:
        return json.load(file)

@admin_user_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_data(user_id):
    """Retrieve user profile, products, wishlist, and ratings."""
    try:
        accounts_db = load_json(DB_PATH_ACCOUNTS)
        wishlist_db = load_json(DB_PATH_WISHLIST)
        products_db = load_json(DB_PATH_PRODUCTS)
        ratings_db = load_json(DB_PATH_RATINGS)

        account = accounts_db.get(str(user_id))
        if not account:
            return jsonify({"error": "User not found"}), 404

        # Fetch wishlist products
        wishlist_products = wishlist_db.get(str(user_id), [])

        wishlist_details = [
            {"id": product_id, "name": products_db.get(product_id, {}).get("name", "Unknown"), "image": products_db.get(product_id, {}).get("image_url", ""), "tags": products_db.get(product_id, {}).get("tags", [])}
            for product_id in wishlist_products
        ]

        # Fetch products listed by the user
        user_products = [
            product for product in products_db.values() if str(product.get("customer_id")) == str(user_id)
        ]

        # Fetch ratings given by the user
        user_ratings = ratings_db.get(str(user_id), {})

        # Prepare response
        user_data = {
            "id": account.get("id"),
            "name": account.get("username"),
            "email": account.get("email"),
            "pfp": account.get("pfp", DEFAULT_PFP_URL),
            "products": user_products,
            "wishlist": wishlist_details,
            "ratings": user_ratings,
            "disabled": account.get("disabled", False),
            "disabled_until": account.get("disabled_until", None),
        }

        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500