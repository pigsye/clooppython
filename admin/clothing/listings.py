import os
import json
from flask import Blueprint, jsonify, request

# Blueprint for products
admin_listings_bp = Blueprint("listings", __name__, url_prefix="/products")

# Paths to the database and upload folder
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products.json")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts.json")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../../api/uploads")

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def load_json(db_path):
    if not os.path.exists(db_path):
        return {}
    with open(db_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(db_path, data):
    with open(db_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@admin_listings_bp.route('/listing/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        products_db = load_json(DB_PATH_PRODUCTS)
        accounts_db = load_json(DB_PATH_ACCOUNTS)

        product = products_db.get(str(product_id))
        if not product:
            return jsonify({"error": "Product not found"}), 404

        customer_id = str(product.get("customer_id", "Unknown"))
        customer_username = accounts_db.get(customer_id, {}).get("username", "Unknown")

        response = {
            "id": str(product_id),
            "name": product.get("name", "Unknown"),
            "tags": product.get("tags", []),
            "description": product.get("description", ""),
            "customer_id": product.get("customer_id", "Unknown"),
            "username": customer_username,
            "img_url": product.get("image_url", None),
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_listings_bp.route('/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    try:
        products_db = load_json(DB_PATH_PRODUCTS)

        if str(product_id) not in products_db:
            return jsonify({"error": "Product not found"}), 404

        product = products_db[str(product_id)]
        name = request.form.get("name")
        customer_id = request.form.get("customer_id")
        tags = request.form.get("tags")

        if name:
            product["name"] = name
        if customer_id:
            product["customer_id"] = int(customer_id)
        if tags:
            product["tags"] = tags.split(",")

        if "image" in request.files:
            image = request.files["image"]
            if image and allowed_file(image.filename):
                image_filename = f"product_{product_id}.jpg"
                image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                image.save(image_path)
                product["image_url"] = f"/uploads/{image_filename}"

        products_db[str(product_id)] = product
        save_json(DB_PATH_PRODUCTS, products_db)

        return jsonify({"message": "Product updated successfully!", "product": product}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_listings_bp.route('/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        products_db = load_json(DB_PATH_PRODUCTS)

        if str(product_id) not in products_db:
            return jsonify({"error": "Product not found"}), 404

        del products_db[str(product_id)]
        save_json(DB_PATH_PRODUCTS, products_db)

        image_filename = f"product_{product_id}.jpg"
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

        return jsonify({"message": "Product deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500