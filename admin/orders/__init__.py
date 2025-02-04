from flask import Blueprint

from .orders import admin_orders_bp

admin_order_bp = Blueprint("admin_order", __name__, url_prefix="/api/admin")

admin_blueprints = [
    admin_orders_bp
]

for bp in admin_blueprints:
    admin_order_bp.register_blueprint(bp)