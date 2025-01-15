import os
import shelve
import time
from flask import Blueprint, jsonify

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

# Define the path to the database folder
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")

# Define paths to individual database files
DB_PATH_ACCOUNT = os.path.join(DB_FOLDER, "accounts")
DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products")
DB_PATH_WISHLIST = os.path.join(DB_FOLDER, "wishlist")
DB_PATH_RATINGS = os.path.join(DB_FOLDER, "ratings")

DEFAULT_PFP_URL = "/account.svg"

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user_data(user_id):
    try:
        # Fetch account information
        with shelve.open(DB_PATH_ACCOUNT, writeback=True) as account_db:
            account = account_db.get(str(user_id))
            if not account:
                return jsonify({"error": "User not found"}), 404

        # Fetch products in the user's wishlist
        wishlist_products = []
        with shelve.open(DB_PATH_WISHLIST) as wishlist_db:
            for product_id, user_ids in wishlist_db.items():
                if str(user_id) in user_ids:  # Check if user_id is in the wishlist
                    wishlist_products.append(product_id)

        # Fetch product details from products.db
        wishlist_details = []
        with shelve.open(DB_PATH_PRODUCTS) as products_db:
            for product_id in wishlist_products:
                product = products_db.get(product_id)
                if product:
                    wishlist_details.append({
                        "id": product["id"],
                        "name": product["name"],
                        "image": product.get("image_url", ""),
                        "tags": product.get("tags", [])
                    })

        # Fetch products listed by the user
        user_products = []
        with shelve.open(DB_PATH_PRODUCTS) as products_db:
            for product_id, product in products_db.items():
                if product["customer_id"] == user_id:  # Match user ID
                    user_products.append(product)

        # Fetch ratings given by the user
        with shelve.open(DB_PATH_RATINGS) as ratings_db:
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
            "disabled_until": account.get("disabled_until", None)
        }

        return jsonify(user_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500