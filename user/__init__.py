from flask import Blueprint

from .products import user_products_bp
from .tags import user_tags_bp
from .feedback import user_feedback_bp
from .logs import user_logs_bp
from .accounts import user_accounts_bp
from .submission import user_submissions_bp

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

user_blueprints = [
    user_products_bp,
    user_tags_bp,
    user_feedback_bp,
    user_logs_bp,
    user_accounts_bp,
    user_submissions_bp
]
 
for bp in user_blueprints:
    user_bp.register_blueprint(bp)