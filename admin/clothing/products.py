import os
import shelve
from flask import Blueprint, jsonify, request

admin_products_bp = Blueprint('products', __name__)

# Define database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products")
DB_PATH_ACCOUNT = os.path.join(DB_FOLDER, "accounts")


@admin_products_bp.route('/products', methods=['GET'])
def get_all_products():
    """
    Get all products from the products database and return only selected fields.
    """
    try:
        final_products = []
        with shelve.open(DB_PATH_PRODUCTS) as products_db:
            for customer_id, product in products_db.items():

                # Get username from accounts.db
                with shelve.open(DB_PATH_ACCOUNT) as accounts_db:
                    customer_data = accounts_db.get(str(product.get("customer_id")))
                    if not customer_data:
                        continue

                    customer_username = customer_data.get("username", "Unknown")

                # Add product to the final list
                final_products.append({
                    "id": product.get("id"),
                    "name": product.get("name"),
                    "username": customer_username,
                    "image_url": product.get("image_url", ""),
                })

        # Sort the products by ID
        final_products = sorted(final_products, key=lambda x: x["id"])

        print(final_products)
        return jsonify(final_products), 200

    except Exception as e:
        print(f"DEBUG: Error occurred: {str(e)}")  # Debug
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@admin_products_bp.route('/create', methods=['POST'])
def create_product():
    """
    Create a new product with the given name and owner (customer ID).
    """
    try:
        data = request.json
        name = data.get("name")
        customer_id = data.get("customer_id")

        if not name or not customer_id:
            return jsonify({"error": "Name and customer ID are required"}), 400

        with shelve.open(DB_PATH_PRODUCTS, writeback=True) as products_db:
            new_id = max([int(key) for key in products_db.keys()] or [0]) + 1
            new_product = {
                "id": new_id,
                "name": name,
                "customer_id": int(customer_id),
                "tags": [],
                "image_url": "",
            }
            products_db[str(new_id)] = new_product

        return jsonify({"message": "Product created successfully!", "product": new_product}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500