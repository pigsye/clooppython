from flask import Blueprint

from .tags import admin_tags_bp

admin_tag_bp = Blueprint("admin_tag", __name__, url_prefix="/api/admin")

admin_blueprints = [
    admin_tags_bp
]

for bp in admin_blueprints:
    admin_tag_bp.register_blueprint(bp)