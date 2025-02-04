from flask import Blueprint

from .products import user_products_bp

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

user_blueprints = [
    user_products_bp
]
 
for bp in user_blueprints:
    user_bp.register_blueprint(bp)