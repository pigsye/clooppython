import os
import json
from flask import Blueprint, jsonify, request

admin_products_bp = Blueprint('products', __name__)

DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products.json")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts.json")

def load_json(db_path):
    if not os.path.exists(db_path):
        return {}
    with open(db_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(db_path, data):
    with open(db_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@admin_products_bp.route('/products', methods=['GET'])
def get_all_products():
    try:
        products_db = load_json(DB_PATH_PRODUCTS)
        accounts_db = load_json(DB_PATH_ACCOUNTS)

        final_products = []
        for product in products_db.values():
            customer_data = accounts_db.get(str(product.get("customer_id")))
            customer_username = customer_data.get("username", "Unknown") if customer_data else "Unknown"

            final_products.append({
                "id": product.get("id"),
                "name": product.get("name"),
                "username": customer_username,
                "image_url": product.get("image_url", ""),
            })

        final_products = sorted(final_products, key=lambda x: x["id"])
        return jsonify(final_products), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_products_bp.route('/create', methods=['POST'])
def create_product():
    try:
        data = request.json
        name = data.get("name")
        customer_id = data.get("customer_id")

        if not name or not customer_id:
            return jsonify({"error": "Name and customer ID are required"}), 400

        products_db = load_json(DB_PATH_PRODUCTS)
        new_id = max([int(k) for k in products_db.keys()] or [0]) + 1

        new_product = {
            "id": new_id,
            "name": name,
            "customer_id": int(customer_id),
            "tags": [],
            "image_url": "",
        }

        products_db[str(new_id)] = new_product
        save_json(DB_PATH_PRODUCTS, products_db)

        return jsonify({"message": "Product created successfully!", "product": new_product}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500