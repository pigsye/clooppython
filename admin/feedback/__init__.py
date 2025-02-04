from flask import Blueprint

from .feedbacks import admin_feedbacks_bp

admin_feedback_bp = Blueprint("admin_feedback", __name__, url_prefix="/api/admin")

admin_blueprints = [
    admin_feedbacks_bp
]

for bp in admin_blueprints:
    admin_feedback_bp.register_blueprint(bp)