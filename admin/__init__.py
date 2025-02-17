from flask import Blueprint

from .accounts import admin_account_bp
from .clothing import admin_clothing_bp
from .feedback import admin_feedback_bp
from .logs import admin_log_bp
from .orders import admin_order_bp
from .tags import admin_tag_bp

admin_bp = Blueprint("admin_logs", __name__)

admin_blueprints = [
    admin_account_bp,
    admin_clothing_bp,
    admin_feedback_bp,
    admin_log_bp,
    admin_order_bp,
    admin_tag_bp
]

for bp in admin_blueprints:
    admin_bp.register_blueprint(bp)