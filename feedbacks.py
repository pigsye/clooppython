import os
import shelve
from flask import Blueprint, jsonify, request

feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')

# Define database paths
DB_FOLDER = os.path.join(os.path.dirname(__file__), "db")
DB_PATH_FEEDBACK = os.path.join(DB_FOLDER, "feedback")
DB_PATH_ACCOUNTS = os.path.join(DB_FOLDER, "accounts")


@feedback_bp.route('/', methods=['GET'])
def get_all_feedbacks():
    """
    Fetch all feedbacks with user IDs resolved to usernames.
    """
    try:
        feedback_list = []

        # Read account data for username resolution
        with shelve.open(DB_PATH_ACCOUNTS) as accounts_db:
            account_usernames = {
                user_id: account.get("username", f"User {user_id}")
                for user_id, account in accounts_db.items()
            }

        # Fetch all feedback
        with shelve.open(DB_PATH_FEEDBACK) as feedback_db:
            for feedback_id, feedback in feedback_db.items():
                feedback_list.append({
                    "id": feedback_id,
                    "user_id": feedback["user_id"],
                    "username": account_usernames.get(str(feedback["user_id"]), "Unknown"),
                    "feedback": feedback["feedback"],
                })

        return jsonify(feedback_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/<int:feedback_id>', methods=['GET'])
def get_feedback_detail(feedback_id):
    """
    Fetch details of a specific feedback.
    """
    try:
        # Read account data for username resolution
        with shelve.open(DB_PATH_ACCOUNTS) as accounts_db:
            account_usernames = {
                user_id: account.get("username", f"User {user_id}")
                for user_id, account in accounts_db.items()
            }

        # Fetch feedback by ID
        with shelve.open(DB_PATH_FEEDBACK) as feedback_db:
            feedback = feedback_db.get(str(feedback_id))
            if not feedback:
                return jsonify({"error": "Feedback not found"}), 404

            feedback_detail = {
                "id": feedback_id,
                "user_id": feedback["user_id"],
                "username": account_usernames.get(str(feedback["user_id"]), "Unknown"),
                "feedback": feedback["feedback"],
            }

        return jsonify(feedback_detail), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/delete', methods=['POST'])
def delete_feedback():
    """
    Delete a feedback by its ID.
    """
    try:
        data = request.json
        feedback_id = str(data.get("id"))

        if not feedback_id:
            return jsonify({"error": "Missing feedback ID"}), 400

        with shelve.open(DB_PATH_FEEDBACK, writeback=True) as feedback_db:
            if feedback_id in feedback_db:
                del feedback_db[feedback_id]
                return jsonify({"message": "Feedback deleted successfully"}), 200
            else:
                return jsonify({"error": "Feedback not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/create', methods=['POST'])
def create_feedback():
    """
    Create a new feedback entry.
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        feedback_text = data.get("feedback")

        if not user_id or not feedback_text:
            return jsonify({"error": "User ID and feedback are required"}), 400

        with shelve.open(DB_PATH_ACCOUNTS) as accounts_db:
            if str(user_id) not in accounts_db:
                return jsonify({"error": f"User with ID {user_id} not found"}), 404

        with shelve.open(DB_PATH_FEEDBACK, writeback=True) as feedback_db:
            # Generate a new feedback ID
            feedback_id = max((int(k) for k in feedback_db.keys()), default=0) + 1

            # Create and save the feedback
            new_feedback = {
                "user_id": int(user_id),
                "feedback": feedback_text,
            }
            feedback_db[str(feedback_id)] = new_feedback

        return jsonify({
            "message": "Feedback created successfully!",
            "feedback": {
                "id": feedback_id,
                "user_id": user_id,
                "feedback": feedback_text,
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/update', methods=['POST'])
def update_feedback():
    """
    Update an existing feedback entry, including the user ID and feedback text.
    """
    try:
        data = request.json
        feedback_id = str(data.get("id"))
        new_user_id = data.get("user_id")
        new_feedback_text = data.get("feedback")

        if not feedback_id or not new_user_id or not new_feedback_text:
            return jsonify({"error": "Feedback ID, user ID, and feedback text are required"}), 400

        with shelve.open(DB_PATH_FEEDBACK, writeback=True) as feedback_db:
            if feedback_id not in feedback_db:
                return jsonify({"error": "Feedback not found"}), 404

            # Update the feedback entry
            feedback_db[feedback_id]["user_id"] = new_user_id
            feedback_db[feedback_id]["feedback"] = new_feedback_text

        return jsonify({"message": "Feedback updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
