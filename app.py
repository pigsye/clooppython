from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
from Accounts.updateinformation import update_bp
from Accounts.account import accounts_bp
from Accounts.reports import reports_bp
from Accounts.user import user_bp
from Accounts.profiles import profile_bp
from Accounts.createaccount import createaccount_bp
from Accounts.account_stats import account_status_bp
from Clothing.products import products_bp
from Clothing.listings import listings_bp
from Clothing.submissions import clothing_bp
from Tags.tags import tags_bp
from orders import orders_bp
from feedbacks import feedback_bp
from logs import logs_bp

sys.path.append(os.path.join(os.path.dirname(__file__), "Accounts"))

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(user_bp)
app.register_blueprint(createaccount_bp)
app.register_blueprint(accounts_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(update_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(account_status_bp)
app.register_blueprint(products_bp)
app.register_blueprint(listings_bp)
app.register_blueprint(clothing_bp)
app.register_blueprint(tags_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(logs_bp)

CORS(app)

# Define the upload folders
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "api/uploads")
PRODUCTS_FOLDER = os.path.join(UPLOAD_FOLDER, "products")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PRODUCTS_FOLDER"] = PRODUCTS_FOLDER

# Ensure the directories exist
os.makedirs(PRODUCTS_FOLDER, exist_ok=True)

# Serve static files
app.add_url_rule('/uploads/<path:filename>', 'uploads', lambda filename: send_from_directory(UPLOAD_FOLDER, filename))
app.add_url_rule('/uploads/products/<path:filename>', 'products', lambda filename: send_from_directory(PRODUCTS_FOLDER, filename))

# Example route to test the server
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask backend!"})


if __name__ == '__main__':
    app.run(debug=True)