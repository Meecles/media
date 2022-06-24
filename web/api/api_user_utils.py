import secrets
import string

from flask import Blueprint, request

from auth.user_manager import get_auth_user
from utils import user_utils, sanitization, authentication
from utils.db_config import db

mod = Blueprint('api_user_utils', __name__)
denied = {"success": False}


def gen_pass():
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for i in range(12))


def get_valid_roles():
    valid_roles = []
    db_perms = db["permissions"].find({"type": "role"})
    for role in db_perms:
        protected = "protected" in role and role["protected"]
        if not protected:
            valid_roles.append(role["_id"])
    return valid_roles


@mod.route("/api/users/list", methods=["GET"])
def user_list():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_permission("api.users.list"):
        return denied

    db_users = db["users"].find({})
    if db_users is None:
        return {"success": False, "reason": "No users found. (Even you!)"}

    valid_roles = []
    db_perms = db["permissions"].find({"type": "role"})
    for role in db_perms:
        valid_roles.append(role["_id"])

    users = []
    for u in db_users:
        mfa_enabled = "mfa_enabled" in u and u["mfa_enabled"]
        mfa_required = "mfa_required" in u and u["mfa_required"]
        version = u["ui_version"] if "ui_version" in u else "N/A"
        users.append({
            "id": u["_id"],
            "username": u["username"],
            "mfa_enabled": mfa_enabled,
            "mfa_required": mfa_required,
            "roles": u["roles"],
            "valid_roles": valid_roles,
            "ui_version": version
        })

    return {"success": True, "users": users}


def update_username(update_user, username):

    if update_user["username"] == username:
        return None

    username = username.lower()
    existing = db["users"].find_one({"username": username})
    if existing is not None:
        return "A user with this username already exists!"

    update_user["username"] = username
    uid = update_user["_id"]
    db["users"].find_one_and_replace({"_id": uid}, update_user)

    return None


@mod.route("/api/users/disable_mfa", methods=["POST"])
def user_disable_mfa():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_permission("profile.mfa.disable.other"):
        return denied
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except Exception as e:
        return {"success": False, "reason": "No data sent"}

    if "id" not in data:
        return {"success": False, "reason": "Id not provided in data"}
    if not isinstance(data["id"], str):
        return {"success": False, "reason": "id is an invalid type. Expecting string"}

    db_user = db["users"].find_one({"_id": data["id"]})
    if db_user is None:
        return {"success": False, "reason": "User with that ID was not found"}

    mfa_enabled = "mfa_enabled" in db_user and db_user["mfa_enabled"]
    if not mfa_enabled:
        return {"success": False, "reason": "MFA is already disabled!"}

    db_user["mfa_enabled"] = False
    db["users"].find_one_and_replace({"_id": data["id"]}, db_user)

    return {"success": True}


@mod.route("/api/users/edit", methods=["POST"])
def user_edit():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_permission("api.users.edit"):
        return denied
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except Exception as e:
        return {"success": False, "reason": "No data sent"}

    if "id" not in data:
        return {"success": False, "reason": "You must provide the user ID you wish to update"}

    if not isinstance(data["id"], str):
        return {"success": False, "reason": "id is an invalid type. Expecting string"}

    editable_values = ["username", "mfa_required", "mfa_enabled", "roles"]
    for key in data:
        if key != "id" and key not in editable_values:
            return {"success": False, "reason": "Cannot edit this data!"}

    update_user = db["users"].find_one({"_id": data["id"]})
    if update_user is None:
        return {"success": False, "reason": "Failed to find user to update"}

    if "username" in data:
        username = data["username"]
        if not isinstance(username, str):
            return {"success": False, "reason": "Username is invalid type"}
        fail = update_username(update_user, username)
        if fail is not None:
            return {"success": False, "reason": fail}

    if "mfa_required" in data:
        mfa_required = data["mfa_required"]
        if not isinstance(mfa_required, bool):
            return {"success": False, "reason": "mfa_required is invalid type"}
        update_user["mfa_required"] = mfa_required

    if "mfa_enabled" in data:
        mfa_enabled = data["mfa_enabled"]
        if not isinstance(mfa_enabled, bool):
            return {"success": False, "reason": "mfa_enabled is invalid type"}
        if not mfa_enabled:
            update_user["mfa_enabled"] = False

    if "roles" in data:
        if all(isinstance(n, str) for n in data["roles"]):
            roles = data["roles"]
            valid_roles = get_valid_roles()
            valid = True
            update_roles = []
            for role in roles:
                if role not in valid_roles:
                    valid = False
                    break
                if role not in update_roles:
                    update_roles.append(role)
            if valid:
                update_user["roles"] = update_roles

    db["users"].find_one_and_replace({"_id": data["id"]}, update_user)

    return {"success": True}


@mod.route("/api/users/delete/<user_id>", methods=["POST"])
def user_delete(user_id):
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_permission("api.users.delete"):
        return denied

    if not isinstance(user_id, str) or user.get_id() == user_id:
        return {"success": False, "reason": "Cannot delete self"}

    to_delete = db["users"].find_one({"_id": user_id})
    if to_delete is None:
        return {"success": False, "reason": "User with this ID does not exist"}

    db["users"].delete_one({"_id": user_id})

    return {"success": True}


@mod.route("/api/users/create", methods=["POST"])
def user_create():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_permission("api.users.create"):
        return denied
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except Exception as e:
        return {"success": False, "reason": "No data sent"}

    reqs = ["username", "roles"]
    for req in reqs:
        if req not in data:
            return {"success": False, "reason": "Not enough information sent!"}

    valid_roles = get_valid_roles()

    username = data["username"].lower()
    valid_user = sanitization.username_valid(username)
    if not valid_user:
        return {"success": False, "reason": "Username must be between 3 and 16 characters long, and alphanumeric"}
    existing = db["users"].find_one({"username": username})
    if existing is not None:
        return {"success": False, "reason": "A user with this username already exists!"}
    password = gen_pass()
    roles = []
    for role in data["roles"]:
        if role in valid_roles:
            roles.append(role)

    user_utils.create_user(username, password, roles, True)

    return {"success": True, "password": password}


@mod.route("/api/users/reset_pw/<user_id>", methods=["POST"])
def reset_password(user_id):
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_permission("api.users.edit"):
        return denied

    to_reset = db["users"].find_one({"_id": user_id})
    if to_reset is None:
        return {"success": False, "reason": "User with this ID does not exist"}

    password = gen_pass()
    authentication.reset_pw(user_id, password)

    return {"success": True, "password": password}


