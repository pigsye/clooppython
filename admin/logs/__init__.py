from flask import Blueprint

from .logs import admin_logs_bp

admin_log_bp = Blueprint("admin_log" , __name__, url_prefix="/api/admin")

admin_blueprints = [
    admin_logs_bp
]

for bp in admin_blueprints:
    admin_log_bp.register_blueprint(bp)