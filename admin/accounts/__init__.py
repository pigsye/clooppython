from flask import Blueprint

from .account_stats import admin_account_status_bp
from .account import admin_accounts_bp
from .createaccount import admin_createaccount_bp
from .profiles import admin_profile_bp
from .reports import admin_reports_bp
from .updateinformation import admin_update_bp
from .user import admin_user_bp

admin_account_bp = Blueprint("admin_account", __name__, url_prefix="/api/admin")

admin_blueprints = [
    admin_account_status_bp,
    admin_accounts_bp,
    admin_createaccount_bp,
    admin_profile_bp,
    admin_reports_bp,
    admin_update_bp,
    admin_user_bp
]

for bp in admin_blueprints:
    admin_account_bp.register_blueprint(bp)