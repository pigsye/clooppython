from flask import Blueprint, jsonify
import os
import shelve

user_products_bp = Blueprint("user_products", __name__)

# Database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products")

@user_products_bp.route("/products", methods=["GET"])
def get_products():
    """
    Fetch all products from the database in numerical order.
    """
    try:
        with shelve.open(DB_PATH_PRODUCTS) as db:
            # Sort keys numerically and retrieve products in order
            products = [db[key] for key in sorted(db.keys(), key=int)]

        return jsonify({"products": products}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500