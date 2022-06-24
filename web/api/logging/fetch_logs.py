from flask import Blueprint

from auth.user_manager import get_auth_user
from utils.db_config import db

mod = Blueprint('api_fetch_logs', __name__)
denied = {"success": False}


@mod.route("/api/logs/<l_type>/past/<count>")
def past_ct(l_type, count):
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["logs.top"]):
        return denied

    try:
        count = int(count)
    except Exception as e:
        return {"success": False, "reason": "Invalid integer"}

    logs = [log for log in db["logs"].find({"type": l_type}).limit(count)]

    return {"success": True, "logs": logs}


@mod.route("/api/logs/self-login")
def self_login():
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["logs.loginself"]):
        return denied

    ips = []

    logs = [log for log in db["logs"].find({"type": "login"}).limit(15)]
    for log in logs:
        ip = log["ip"] if "ip" in log else "N/A"
        if ip not in ips:
            ips.append(ip)

    return {"success": True, "recent_ip": ips}
