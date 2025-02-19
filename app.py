from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from flask_mail import Mail

app = Flask(__name__)
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "the-29th-of-september"  # Change this to a strong secret key

# ✅ Email Configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"  # Change this if using another provider
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "eayancheong@gmail.com"  # Your email
app.config["MAIL_PASSWORD"] = "gsdx dxps bqzr jnsv"  # Use an App Password for security
app.config["MAIL_DEFAULT_SENDER"] = "eayancheong@gmail.com"  # Default sender

mail = Mail(app)

from admin import admin_bp
from user import user_bp

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
    return jsonify({"yes": "it works"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)