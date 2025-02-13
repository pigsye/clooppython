from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
from admin import admin_bp
from user import user_bp


app = Flask(__name__)

# Register Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

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