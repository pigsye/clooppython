from flask import Blueprint, jsonify
import os
import shelve

user_products_bp = Blueprint("user_products", __name__)

# Database paths
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products")
DB_PATH_WISHLIST = os.path.join(DB_FOLDER, "wishlist")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts")

def get_username(user_id):
    """
    Fetch username from accounts database.
    """
    try:
        with shelve.open(DB_PATH_ACCOUNTS) as db:
            user_data = db.get(str(user_id), {})
            return user_data.get("username", f"User {user_id}")
    except Exception as e:
        return f"User {user_id}"  # Fallback if database error occurs

@user_products_bp.route("/products", methods=["GET"])
def get_products():
    """
    Fetch all products from the database in numerical order, including seller usernames.
    """
    try:
        with shelve.open(DB_PATH_PRODUCTS) as db:
            products = []
            for key in sorted(db.keys(), key=int):
                product = db[key]
                product["seller_username"] = get_username(product["customer_id"])  # Fetch username
                products.append(product)

        return jsonify({"products": products}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@user_products_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """
    Fetch a single product by ID, including the seller's username.
    """
    try:
        with shelve.open(DB_PATH_PRODUCTS) as db:
            product = db.get(str(product_id))

        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Fetch seller username
        product["seller_username"] = get_username(product["customer_id"])

        return jsonify({"product": product}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@user_products_bp.route("/wishlist/<int:product_id>", methods=["POST"])
def toggle_wishlist(product_id):
    """
    Adds or removes a product from the wishlist for user 1 (assumption until login is implemented).
    """
    try:
        user_id = "1"  # Assume user ID 1 for now
        print(f"📌 DEBUG: Toggling wishlist for product {product_id} and user {user_id}")

        with shelve.open(DB_PATH_WISHLIST, writeback=True) as db:
            print("📌 DEBUG: Opened wishlist database")

            if str(product_id) not in db:
                db[str(product_id)] = []
                print(f"📌 DEBUG: Created new wishlist entry for product {product_id}")

            wishlist = db[str(product_id)]  # Store wishlist in a temporary variable
            print(f"📌 DEBUG: Current wishlist for product {product_id}: {wishlist}")

            if user_id in wishlist:
                wishlist.remove(user_id)
                action = "removed from"
                print(f"📌 DEBUG: User {user_id} removed from wishlist")
            else:
                wishlist.append(user_id)
                action = "added to"
                print(f"📌 DEBUG: User {user_id} added to wishlist")

            db[str(product_id)] = wishlist  # Store updated wishlist back in the database
            print(f"📌 DEBUG: Updated wishlist for product {product_id}: {wishlist}")

            # Store updated status before closing the database
            wishlist_status = user_id in wishlist

        return jsonify({
            "message": f"Product {product_id} {action} wishlist for user {user_id}",
            "wishlist_status": wishlist_status
        }), 200

    except Exception as e:
        print(f"❌ DEBUG ERROR: {str(e)}")  # Print error for debugging
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500