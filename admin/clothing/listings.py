import os
import shelve
from flask import Blueprint, jsonify, request

# Blueprint for products
admin_listings_bp = Blueprint("listings", __name__)

# Paths to the database and upload folder
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../../api/uploads")

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@admin_listings_bp.route('/listing/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Fetch details of a specific product by its ID, including the owner's username and product image URL.
    """
    try:
        with shelve.open(DB_PATH_PRODUCTS) as products_db:
            product = products_db.get(str(product_id))  # Fetch the product
            if not product:
                return jsonify({"error": "Product not found"}), 404

            # Fetch the owner's username from the accounts database
            with shelve.open(DB_PATH_ACCOUNTS) as accounts_db:
                customer_id = str(product.get("customer_id", "Unknown"))
                customer_data = accounts_db.get(customer_id)
                customer_username = customer_data.get("username", "Unknown") if customer_data else "Unknown"

            # Include the image URL if it exists
            img_url = product.get("image_url", None)  # Use None as the default if img_url is not present

            # Construct the response
            response = {
                "id": str(product_id),  # Ensure ID is always a string
                "name": product.get("name", "Unknown"),  # Provide a fallback if name is missing
                "tags": product.get("tags", []),  # Default to an empty list
                "description": product.get("description", ""),  # Default to an empty string
                "customer_id": product.get("customer_id", "Unknown"),  # Provide a fallback
                "username": customer_username,  # Include the username in the response
                "img_url": img_url,  # Include the image URL if available
            }
        print(response)
        return jsonify(response), 200

    except Exception as e:
        print(f"ERROR: {e}")  # Log the error for debugging
        return jsonify({"error": str(e)}), 500


@admin_listings_bp.route('/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    """
    Update the product's name, user ID, tags, or image.
    """
    try:
        # Open the products database
        with shelve.open(DB_PATH_PRODUCTS, writeback=True) as products_db:
            # Fetch the product
            product = products_db.get(str(product_id))
            if not product:
                return jsonify({"error": "Product not found"}), 404

            # Update the product name
            name = request.form.get("name")
            if name:
                product["name"] = name

            # Update the customer ID
            customer_id = request.form.get("customer_id")
            if customer_id:
                product["customer_id"] = int(customer_id)

            # Update tags
            tags = request.json.get("tags")
            if tags and isinstance(tags, list):
                product["tags"] = tags

            # Handle image upload
            if "image" in request.files:
                image = request.files["image"]
                if image:
                    # Save the image using the naming convention
                    image_filename = f"product_{product_id}.jpg"
                    image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                    image.save(image_path)
                    product["image_url"] = f"/uploads/{image_filename}"

            # Save changes to the database
            products_db[str(product_id)] = product

        return jsonify({"message": "Product updated successfully!"}), 200

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 500

@admin_listings_bp.route('/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Delete a product by its ID.
    """
    try:
        with shelve.open(DB_PATH_PRODUCTS, writeback=True) as products_db:
            # Check if the product exists
            if str(product_id) not in products_db:
                return jsonify({"error": "Product not found"}), 404

            # Delete the product
            del products_db[str(product_id)]

        # Optionally delete the image associated with the product
        image_filename = f"product_{product_id}.jpg"
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

        return jsonify({"message": "Product deleted successfully!"}), 200

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 500
