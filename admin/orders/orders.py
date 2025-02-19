import os
import json
from flask import Blueprint, jsonify, request

admin_orders_bp = Blueprint("orders", __name__)

DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_ORDERS = os.path.join(DB_FOLDER, "orders.json")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts.json")

def load_json(db_path):
    if not os.path.exists(db_path):
        return {}
    with open(db_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(db_path, data):
    with open(db_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@admin_orders_bp.route('/', methods=['GET'])
def get_all_orders():
    try:
        orders_db = load_json(DB_PATH_ORDERS)
        accounts_db = load_json(DB_PATH_ACCOUNTS)

        orders = [
            {
                "id": int(order_id),
                "user": accounts_db.get(str(order.get("user_id")), {}).get("username", "Unknown"),
            }
            for order_id, order in orders_db.items()
        ]

        return jsonify(sorted(orders, key=lambda x: x["id"])), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_orders_bp.route('/create', methods=['POST'])
def create_order():
    try:
        data = request.json
        user_id = str(data.get("user_id"))
        shipping_address = data.get("shipping_address")

        if not user_id or not shipping_address:
            return jsonify({"error": "User ID and shipping address are required"}), 400

        orders_db = load_json(DB_PATH_ORDERS)
        new_order_id = str(max([int(k) for k in orders_db.keys()] or [0]) + 1)

        new_order = {
            "user_id": user_id,
            "shipping_address": shipping_address,
            "products": data.get("products", []),
        }

        orders_db[new_order_id] = new_order
        save_json(DB_PATH_ORDERS, orders_db)

        return jsonify({"message": "Order created successfully!", "order_id": new_order_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500