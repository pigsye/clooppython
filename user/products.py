from flask import Blueprint, jsonify, request
import os
import json
from flask_jwt_extended import jwt_required, get_jwt_identity

user_products_bp = Blueprint("user_products", __name__)

# Database paths
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products.json")
DB_PATH_WISHLIST = os.path.join(DB_FOLDER, "wishlist.json")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts.json")

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

def get_username(user_id):
    """Fetch username from accounts database."""
    accounts_db = load_json(DB_PATH_ACCOUNTS)
    return accounts_db.get(str(user_id), {}).get("username", f"User {user_id}")

@user_products_bp.route("/products", methods=["GET"])
def get_products():
    """Fetch all products from the database in numerical order, including seller usernames."""
    try:
        products_db = load_json(DB_PATH_PRODUCTS)
        products = []

        for key in sorted(products_db.keys(), key=int):
            product = products_db[key]
            product["seller_username"] = get_username(product["customer_id"])  # Fetch username
            if product.get("is_listed", True):  # Exclude delisted products
                products.append(product)

        return jsonify({"products": products}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@user_products_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Fetch a single product by ID, including the seller's username."""
    try:
        products_db = load_json(DB_PATH_PRODUCTS)
        product = products_db.get(str(product_id))

        if not product:
            return jsonify({"error": "Product not found"}), 404

        product["seller_username"] = get_username(product["customer_id"])
        return jsonify({"product": product}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@user_products_bp.route("/wishlist/<int:product_id>", methods=["POST"])
def toggle_wishlist(product_id):
    """Adds or removes a product from the wishlist for user 1 (assumption until login is implemented)."""
    try:
        user_id = "1"  # Assume user ID 1 for now
        wishlist_db = load_json(DB_PATH_WISHLIST)

        if str(product_id) not in wishlist_db:
            wishlist_db[str(product_id)] = []

        wishlist = wishlist_db[str(product_id)]

        if user_id in wishlist:
            wishlist.remove(user_id)
            action = "removed from"
        else:
            wishlist.append(user_id)
            action = "added to"

        wishlist_db[str(product_id)] = wishlist
        save_json(DB_PATH_WISHLIST, wishlist_db)

        return jsonify({
            "message": f"Product {product_id} {action} wishlist for user {user_id}",
            "wishlist_status": user_id in wishlist
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@user_products_bp.route("/products/<int:product_id>/toggle-listing", methods=["POST"])
@jwt_required()
def toggle_listing(product_id):
    """Toggle a product's listing status (list/unlist). Only the product owner can perform this action."""
    try:
        user = get_jwt_identity()  # Get user from JWT
        user_id = str(user["id"])

        products_db = load_json(DB_PATH_PRODUCTS)
        product = products_db.get(str(product_id))

        if not product:
            return jsonify({"error": "Product not found"}), 404

        if str(product["customer_id"]) != user_id:
            return jsonify({"error": "Permission denied"}), 403

        product["is_listed"] = not product.get("is_listed", True)
        products_db[str(product_id)] = product
        save_json(DB_PATH_PRODUCTS, products_db)

        return jsonify({
            "message": "Product listing status updated",
            "is_listed": product["is_listed"]
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500