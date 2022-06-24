from flask import Blueprint

from auth.user_manager import get_auth_user
from utils.db_config import db

mod = Blueprint('api_user', __name__)
denied = {"success": False}


@mod.route("/api/users")
def get_users():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_any_permission(["api.users.list", "access.users"]):
        return denied

    db_users = db["users"].find({}, ["_id", "username", "name", "mfa_required", "mfa_enabled", "roles"])
    users = [user for user in db_users]

    return {"success": True, "users": users}
