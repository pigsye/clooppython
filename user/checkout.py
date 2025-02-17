import stripe
from flask import Blueprint, jsonify, request
import os
import shelve
from flask_jwt_extended import jwt_required, get_jwt_identity

user_checkout_bp = Blueprint("checkout", __name__)

stripe.api_key = "sk_test_51QtAEpFQvhgt2WZEVLCpAg6NNsTqKY4zesjYyEhFhvJ5ZE43E95X41Z3TgtroIc7IT5xyfxjkM14QkMxjtXcn7TE00E8O4aTv8"

DB_FOLDER = os.path.join(os.path.dirname(__file__), "../db")
DB_PATH_ORDERS = os.path.join(DB_FOLDER, "orders")
DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products")

@user_checkout_bp.route("/cart/products", methods=["POST"])
def get_cart_products():
    """Fetch product details based on product IDs."""
    try:
        data = request.json
        product_ids = data.get("product_ids", [])

        if not product_ids:
            return jsonify({"error": "No products in cart"}), 400

        with shelve.open(DB_PATH_PRODUCTS) as db:
            products = [db[str(pid)] for pid in product_ids if str(pid) in db]
            total_price = sum(product["price"] for product in products)

        return jsonify({"products": products, "total_price": total_price}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@user_checkout_bp.route("/checkout", methods=["POST"])
def create_checkout_session():
    try:
        data = request.json
        line_items = [
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": item["name"]},
                    "unit_amount": int(item["price"] * 100),  # Convert dollars to cents
                },
                "quantity": 1,
            }
            for item in data["items"]
        ]

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/cart",
        )

        return jsonify({"sessionId": session.id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500