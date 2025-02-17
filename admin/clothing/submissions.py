import os
import shelve
from flask import Blueprint, jsonify, request

admin_clothings_bp = Blueprint("clothing", __name__, url_prefix="/clothing")

# Define paths to the database files
DB_FOLDER = os.path.join(os.path.dirname(__file__), "../../db")
DB_PATH_SUBMISSIONS = os.path.join(DB_FOLDER, "submissions")
DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts")


@admin_clothings_bp.route('/submissions', methods=['GET'])
def get_submissions():
    """
    Fetch all pending submissions, resolving customer IDs to usernames.
    """
    try:
        submissions = []
        # Open the submissions and accounts databases
        with shelve.open(DB_PATH_SUBMISSIONS) as submissions_db, shelve.open(DB_PATH_ACCOUNTS) as accounts_db:
            for submission_id, submission in submissions_db.items():
                customer_id = submission.get("customerId")
                customer_name = accounts_db.get(str(customer_id), {}).get("username", "Unknown")  # Resolve username
                submissions.append({
                    "id": submission_id,
                    "customerName": customer_name,
                    "clothing_name": submission.get("clothing_name"),
                    "description": submission.get("description"),
                    "customerId": customer_id,  # Include customer ID for logic
                })
        return jsonify(submissions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_clothings_bp.route('/add', methods=['POST'])
def add_product():
    """
    Add a new product to the products database.
    If the product ID already exists, automatically increment the ID until a unique one is found.
    """
    try:
        data = request.json
        with shelve.open(DB_PATH_PRODUCTS, writeback=True) as products_db:
            # Start with the provided ID
            product_id = int(data["id"])

            # Increment the ID if it already exists
            while str(product_id) in products_db:
                product_id += 1

            # ✅ Ensure the image URL is transferred correctly
            image_url = data.get("image_url")  # Get the image URL

            # Add the new product with the image URL
            new_product = {
                "id": product_id,
                "name": data["name"],
                "customer_id": data["customerId"],
                "tags": data.get("tags", []),
                "wishlisted_users": {},
                "image_url": image_url,  # ✅ Store image URL
            }
            products_db[str(product_id)] = new_product

        return jsonify({"message": f"Product added successfully with ID {product_id}!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_clothings_bp.route('/deletesubmission', methods=['POST'])
def delete_submission():
    """
    Delete a submission after acceptance or rejection.
    """
    try:
        data = request.json
        submission_id = str(data.get("id"))

        if not submission_id:
            return jsonify({"error": "Missing submission ID"}), 400

        with shelve.open(DB_PATH_SUBMISSIONS, writeback=True) as submissions_db:
            if submission_id in submissions_db:
                del submissions_db[submission_id]
                return jsonify({"message": "Submission deleted successfully"}), 200
            else:
                return jsonify({"error": "Submission not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_clothings_bp.route('/addsubmission', methods=['POST'])
def add_submission():
    """
    Add a new submission to the submissions database.
    """
    try:
        data = request.json
        clothing_name = data.get("clothing_name")
        description = data.get("description", "")
        customer_id = data.get("customerId")

        if not clothing_name or not customer_id:
            return jsonify({"error": "Clothing name and customer ID are required"}), 400

        with shelve.open(DB_PATH_SUBMISSIONS, writeback=True) as submissions_db:
            # Generate a new submission ID
            new_submission_id = max(
                (int(k) for k in submissions_db.keys()), default=0
            ) + 1

            # Create the submission object
            new_submission = {
                "clothing_name": clothing_name,
                "description": description,
                "customerId": customer_id,
            }

            # Save the submission to the database
            submissions_db[str(new_submission_id)] = new_submission

        return jsonify({"message": "Submission added successfully!"}), 200

    except Exception as e:
        print(f"Error adding submission: {e}")
        return jsonify({"error": str(e)}), 500


@admin_clothings_bp.route('/editsubmission', methods=['POST'])
def edit_submission():
    """
    Edit an existing clothing submission.
    """
    try:
        data = request.json
        submission_id = str(data.get("id"))

        if not submission_id:
            return jsonify({"error": "Submission ID is required"}), 400

        with shelve.open(DB_PATH_SUBMISSIONS, writeback=True) as submissions_db:
            if submission_id not in submissions_db:
                return jsonify({"error": "Submission not found"}), 404

            # Update the submission
            submissions_db[submission_id].update({
                "clothing_name": data["clothing_name"],
                "description": data["description"],
                "customerId": data["customerId"],  # Update customer ID
            })

        return jsonify({"message": "Submission updated successfully!"}), 200
    except Exception as e:
        print(f"Error editing submission: {e}")
        return jsonify({"error": str(e)}), 500
