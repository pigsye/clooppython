from flask import Blueprint

from .listings import admin_listings_bp
from .products import admin_products_bp
from .submissions import admin_clothings_bp

admin_clothing_bp = Blueprint("admin_clothing", __name__, url_prefix="/api/admin")

admin_blueprints = [
    admin_listings_bp,
    admin_products_bp,
    admin_clothings_bp
]

for bp in admin_blueprints:
    admin_clothing_bp.register_blueprint(bp)