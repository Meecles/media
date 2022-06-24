from datetime import datetime, timedelta

from flask import Blueprint, request

from auth.user_manager import get_auth_user
from utils import otp_utils, time_utils, authentication
from utils.db_config import db

mod = Blueprint('api_profile_utils', __name__)
denied = {"success": False}


@mod.route("/api/mfa/pause", methods=["POST"])
def pause_mfa():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_permission("profile.mfa.pause"):
        return denied

    now = datetime.strptime(time_utils.get_current_datetime(), time_utils.get_date_format())
    future = now + timedelta(hours=1)
    db_user = db["users"].find_one({"_id": user.get_id()})
    if db_user is None:
        return {"success": False, "reason": "An error occurred finding your account"}
    db_user["mfa-paused"] = str(future)
    db["users"].find_one_and_replace({"_id": user.get_id()}, db_user)

    return {"success": True, "until": str(future)}


@mod.route("/api/mfa/initiate")
def initiate_mfa():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_any_permission(["profile.mfa.enable", "profile.all.self"]):
        return denied
    secret = otp_utils.generate_secret()
    user.pending_mfa(secret)
    return {"success": True, "provision": otp_utils.get_provisioning_uri(secret, user.get_username()), "secret": secret}


@mod.route("/api/mfa/disable", methods=["POST"])
def disable_mfa():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_any_permission(["profile.mfa.disable.self", "profile.all.self"]):
        return denied

    mfa_enabled = user.mfa_enabled()
    if not mfa_enabled:
        return {"success": False, "reason": "MFA not enabled"}
    d_user = db["users"].find_one({"_id": user.get_id()})
    d_user["mfa_enabled"] = False
    db["users"].find_one_and_replace({"_id": user.get_uid()}, d_user)
    return {"success": True}


@mod.route("/api/mfa/enable", methods=["POST"])
def enable_mfa():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_any_permission(["profile.mfa.enable", "profile.all.self"]):
        return denied
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except:
        return {"success": False, "reason": "Error, invalid data sent by client"}
    if "token" not in data:
        return {"success": False, "reason": "Error, invalid data sent by client"}
    if user.mfa_enabled():
        return {"success": False, "reason": "MFA is already enabled"}
    token = data["token"]
    pending_secret = user.get_pending_secret()
    if pending_secret is None:
        return {"success": False, "reason": "Error, no mfa initiation"}
    validated = otp_utils.verify_token(pending_secret, token)
    if not validated:
        return {"success": False, "reason": "Your one time token did not match!"}
    d_user = db["users"].find_one({"_id": user.get_id()})
    d_user["mfa_enabled"] = True
    d_user["mfa_token"] = pending_secret
    db["users"].find_one_and_replace({"_id": user.get_uid()}, d_user)
    user.pending_mfa(None)
    return {"success": True}


@mod.route("/api/change_password", methods=["POST"])
def change_password():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_any_permission(["profile.password.change.self", "profile.all.self"]):
        return denied
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except:
        return {"success": False, "reason": "Error, invalid data sent by client"}
    if data is None:
        return {"success": False, "reason": "Error, no data sent by client"}

    if "current" not in data or "new" not in data or "repeat" not in data:
        return {"success": False, "reason": "Error, invalid data sent by client"}

    current = data["current"]
    new = data["new"]
    repeat = data["repeat"]
    if new != repeat:
        return {"success": False, "reason": "New and Confirm passwords do not match!"}
    return authentication.change_pw(user.get_id(), current, new)

