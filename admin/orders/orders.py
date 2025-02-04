import os
import shelve
from flask import Blueprint, jsonify, request

admin_orders_bp = Blueprint("orders", __name__)

# Path to the database files
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_ORDERS = os.path.join(DB_FOLDER, "orders")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts")

@admin_orders_bp.route('/', methods=['GET'])
def get_all_orders():
    """
    Retrieve all orders, sorted by order ID.
    """
    try:
        orders = []
        print("DEBUG: Opening databases...")  # Debug log

        with shelve.open(DB_PATH_ORDERS) as orders_db, shelve.open(DB_PATH_ACCOUNTS) as accounts_db:
            for order_id, order in orders_db.items():
                print(f"DEBUG: Processing order_id {order_id}, order: {order}")  # Debug log

                user_id = str(order.get("user_id"))  # Ensure user_id is a string
                username = accounts_db.get(user_id, {}).get("username", "Unknown User")

                print(f"DEBUG: user_id: {user_id}, username: {username}")  # Debug log

                orders.append({
                    "id": int(order_id),  # Convert to int for proper sorting
                    "user": username,
                })

        # Sort the orders by ID
        sorted_orders = sorted(orders, key=lambda x: x["id"])

        print(f"DEBUG: Sorted orders list: {sorted_orders}")  # Debug log
        return jsonify(sorted_orders), 200
    except Exception as e:
        print(f"ERROR: {e}")  # Log the error
        return jsonify({"error": str(e)}), 500

@admin_orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order_details(order_id):
    """
    Retrieve details of a specific order.
    """
    try:
        with shelve.open(DB_PATH_ORDERS) as orders_db, shelve.open(DB_PATH_ACCOUNTS) as accounts_db:
            order = orders_db.get(str(order_id))
            if not order:
                return jsonify({"error": "Order not found"}), 404

            username = accounts_db.get(str(order["user_id"]), {}).get("username", "Unknown User")

            response = {
                "name": f"Order {order_id}",
                "order_user": username,
                "products": order["products"],
                "shipping_address": order["shipping_address"],
            }

        print(response)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_orders_bp.route('/<int:order_id>/update_user', methods=['POST'])
def update_order_user(order_id):
    """
    Update the user associated with the order.
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        with shelve.open(DB_PATH_ORDERS, writeback=True) as orders_db:
            order = orders_db.get(str(order_id))
            if not order:
                return jsonify({"error": "Order not found"}), 404

            order["user_id"] = user_id
            orders_db[str(order_id)] = order

        return jsonify({"message": "Order user updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_orders_bp.route('/<int:order_id>/update_address', methods=['POST'])
def update_order_address(order_id):
    """
    Update the shipping address for the order.
    """
    try:
        data = request.json
        shipping_address = data.get("shipping_address")
        if not shipping_address:
            return jsonify({"error": "Shipping address is required"}), 400

        with shelve.open(DB_PATH_ORDERS, writeback=True) as orders_db:
            order = orders_db.get(str(order_id))
            if not order:
                return jsonify({"error": "Order not found"}), 404

            order["shipping_address"] = shipping_address
            orders_db[str(order_id)] = order

        return jsonify({"message": "Shipping address updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_orders_bp.route('/<int:order_id>/remove_product', methods=['POST'])
def remove_order_product(order_id):
    """
    Remove a product from the order.
    """
    try:
        data = request.json
        product_name = data.get("product_name")
        if not product_name:
            return jsonify({"error": "Product name is required"}), 400

        with shelve.open(DB_PATH_ORDERS, writeback=True) as orders_db:
            order = orders_db.get(str(order_id))
            if not order:
                return jsonify({"error": "Order not found"}), 404

            order["products"] = [p for p in order["products"] if p["name"] != product_name]
            orders_db[str(order_id)] = order

        return jsonify({"message": f"Product '{product_name}' removed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_orders_bp.route('/create', methods=['POST'])
def create_order():
    """
    Create a new order with a user ID, shipping address, and optional products.
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        shipping_address = data.get("shipping_address")
        product_ids = data.get("products", [])  # Default to an empty list if not provided

        if not user_id or not shipping_address:
            return jsonify({"error": "User ID and shipping address are required"}), 400

        product_list = []  # To store the full product details

        # Fetch product details from products.db
        DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products")
        with shelve.open(DB_PATH_PRODUCTS) as products_db:
            for p_id in product_ids:
                product = products_db.get(p_id)
                if product:
                    product_list.append({
                        "id": p_id,
                        "name": product.get("name", "Unknown Product"),
                    })
                else:
                    return jsonify({"error": f"Product with ID {p_id} not found"}), 404

        with shelve.open(DB_PATH_ORDERS, writeback=True) as orders_db:
            # Generate a new order ID
            new_order_id = max((int(k) for k in orders_db.keys()), default=0) + 1

            # Create the order object
            new_order = {
                "user_id": user_id,
                "shipping_address": shipping_address,
                "products": product_list,
            }

            # Save the new order in the database
            orders_db[str(new_order_id)] = new_order

        return jsonify({
            "message": "Order created successfully!",
            "order": {
                "id": new_order_id,
                "user": user_id,
                "shipping_address": shipping_address,
                "products": product_list,
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_orders_bp.route('/<int:order_id>/delete', methods=['DELETE'])
def delete_order(order_id):
    """
    Delete a specific order by its ID.
    """
    try:
        with shelve.open(DB_PATH_ORDERS, writeback=True) as orders_db:
            if str(order_id) not in orders_db:
                return jsonify({"error": "Order not found"}), 404

            del orders_db[str(order_id)]

        return jsonify({"message": "Order deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
