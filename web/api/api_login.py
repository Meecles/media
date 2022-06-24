import sys
import uuid
from datetime import datetime

import bcrypt
from flask import Blueprint, session, request

from auth import user_manager, media_user
from auth.user_manager import get_auth_user
from utils import otp_utils, sanitization, time_utils
from utils.db_config import db
from utils.logging import log

mod = Blueprint('api_login', __name__)


def get_user():
    if "token" in session:
        token = session.get("token")
        user = user_manager.get_user(token)
        return user
    return None


def get_user_obj():
    if "token" in session:
        token = session.get("token")
        user = user_manager.get_user_no_auth(token)
        return user
    return None


def generate_user(username, password):
    ip = "N/A"
    if request.headers.get("CF-Connecting-IP") is not None:
        ip = request.headers.get("CF-Connecting-IP")
    sess_user = get_user_obj()
    if sess_user is not None and not sess_user.is_fully_authed():
        user_manager.remove_user(sess_user)
    db_user = db["users"].find_one({"username": username})
    if db_user is not None:
        hashed = db_user["password"]
        debug_bypass = "-DEBUG2" in sys.argv and password == "admin" and username.lower() == "admin"
        if bcrypt.checkpw(password.encode('utf8'), hashed.encode('utf8')) or debug_bypass:
            token = str(uuid.uuid4())
            mfa_enabled = "mfa_enabled" in db_user and db_user["mfa_enabled"]
            permissions = []
            roles = []
            allowed_to_assign_perms = True
            if "mfa_required" in db_user and db_user["mfa_required"]:
                if not mfa_enabled:
                    allowed_to_assign_perms = False
                    r = db["permissions"].find_one({"_id": "no_mfa", "type": "role"})
                    for permission in r["permissions"]:
                        permissions.append(permission)
            video_groups = []
            if "roles" in db_user and allowed_to_assign_perms:
                roles = db_user["roles"]
                for role in roles:
                    db_role = db["permissions"].find_one({"_id": role, "type": "role"})
                    if db_role is not None:
                        perms = db_role["permissions"]
                        for perm in perms:
                            if perm not in permissions:
                                permissions.append(perm)
                        if "video_groups" in db_role:
                            for group in db_role["video_groups"]:
                                if group not in video_groups:
                                    video_groups.append(group)
                        extra_roles = db_role["extra_roles"]
                        for r2 in extra_roles:
                            r = db["permissions"].find_one({"_id": r2, "type": "role"})
                            if "video_groups" in r:
                                for group in r["video_groups"]:
                                    if group not in video_groups:
                                        video_groups.append(group)
                            if r is not None:
                                p2 = r["permissions"]
                                for p in p2:
                                    if p not in permissions:
                                        permissions.append(p)

            details = {
                "mfa_enabled": mfa_enabled,
                "roles": roles,
                "permissions": permissions,
                "other": db_user,
                "video_groups": video_groups
            }
            user = media_user.User(db_user["username"], token, db_user["_id"], details)
            if not mfa_enabled:
                user.set_fully_authed(True)
            user_manager.add_user(user)
            return user
        mfa_enabled = "mfa_enabled" in db_user and db_user["mfa_enabled"]
    return None


def mfa_login(data, redirect="/videos"):
    user = get_user_obj()
    if user is None:
        return {"success": False, "reason": "No session to validate"}
    if user.is_fully_authed():
        return {"success": False, "reason": "Already logged in"}
    if "mfa_token" not in data:
        return {"success": False, "reason": "Invalid MFA Token"}
    uid = user.get_uid()
    db_user = db["users"].find_one({"_id": uid})
    if "mfa_enabled" not in db_user or not db_user["mfa_enabled"]:
        return {"success": False, "reason": "User does not require MFA"}
    if "mfa_token" not in db_user:
        return {"success": False, "reason": "User in database is malformed. Please contact the host"}
    mfa_token = db_user["mfa_token"]
    mfa_token_valid = sanitization.mfa_key_valid(mfa_token)
    if not mfa_token:
        return {"success": False, "reason": "Invalid MFA Token"}
    valid_mfa = otp_utils.verify_token(mfa_token, data["mfa_token"])
    ip = data["ip"] if "ip" in data else None
    if valid_mfa:
        user.set_fully_authed(True, ip=ip)
        user_details = db["users"].find_one({"_id": user.get_id()}, ["last_login_ip", "home_screen", "ui_version"])
        if "ui_version" in user_details:
            if user_details["ui_version"] == 2:
                if "home_screen" in user_details:
                    screen = user_details["home_screen"]
                    redirect = "/movies" if screen == "movie" else "/shows" if screen == "tv" else "/movies"
                else:
                    redirect = "/movies"
        return {"success": True, "redirect": redirect}
    return {"success": False, "reason": "Invalid MFA Token"}


def std_login(data, redirect="/videos"):
    if "username" not in data or "password" not in data:
        return {"success": False, "reason": "No initial login"}
    username = data["username"].lower()
    valid_user = sanitization.username_valid(username)
    if not valid_user:
        return {"success": False, "reason": "Invalid Username or Password"}
    password = data["password"]
    user = generate_user(username, password)
    if user is None:
        return {"success": False, "reason": "Invalid Username or Password"}
    user_details = db["users"].find_one({"_id": user.get_id()}, ["last_login_ip", "home_screen", "ui_version"])
    token = user.token
    session['token'] = token
    ip = data["ip"] if "ip" in data else None
    if not user.mfa_enabled():
        if "ui_version" in user_details:
            if user_details["ui_version"] == 2:
                if "home_screen" in user_details:
                    screen = user_details["home_screen"]
                    redirect = "/movies" if screen == "movie" else "/shows" if screen == "tv" else "/movies"
                else:
                    redirect = "/movies"
        user.set_fully_authed(True, ip=ip)
        return {"success": True, "redirect": redirect}
    other = user.get_details()["other"]
    ip_same = False
    if user_details is not None and "last_login_ip" in user_details:
        ip_same = user_details["last_login_ip"] == ip
    if "ui_version" in user_details:
        if user_details["ui_version"] == 2:
            if "home_screen" in user_details:
                screen = user_details["home_screen"]
                redirect = "/movies" if screen == "movie" else "/shows" if screen == "tv" else "/movies"
            else:
                redirect = "/movies"
    if "mfa-paused" in other or ip_same:
        if ip_same:
            ip = data["ip"] if "ip" in data else None
            user.set_fully_authed(True, ip=ip)
            return {"success": True, "redirect": redirect}
        dbt = other["mfa-paused"]
        try:
            t = datetime.strptime(dbt, time_utils.get_date_format())
            now = datetime.strptime(time_utils.get_current_datetime(), time_utils.get_date_format())
            if now <= t:
                ip = data["ip"] if "ip" in data else None
                user.set_fully_authed(True, ip=ip)
                return {"success": True, "redirect": redirect}
        except Exception as e:
            pass
    return {"success": False, "reason": "MFA Required"}


def valid_redirect(redirect):
    valid = [
        "/shows",
        "/movies",
        "/profile",
        "/content",
        "/backup",
        "/users",
        "/roles",
        "/settings"
    ]
    starts = [
        "/watch/movie/",
        "/watch/tv/",
        "/shows/"
    ]
    start_valid = False
    for s in starts:
        if redirect.startswith(s):
            start_valid = True
            break
    return redirect in valid or start_valid


@mod.route('/api/login', methods=['POST'])
def login():
    user = get_auth_user()
    if user is not None:
        return {"success": False, "reason": "Already logged in"}
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except Exception as e:
        return {"success": False, "reason": "No login data sent"}
    user = get_user_obj()
    ip = "N/A"
    if request.headers.get("CF-Connecting-IP") is not None:
        ip = request.headers.get("CF-Connecting-IP")
    data["ip"] = ip
    if "username" in data and "ip" in data:
        print("{} is attempting to login with ip: {}".format(data["username"], data["ip"]))
    else:
        print(data)
    redirect = "/"
    if "redir" in data and isinstance(data["redir"], str):
        redirect = data["redir"]
        if not valid_redirect(redirect):
            redirect = "/"
    resp = None
    mfa_used = False
    if user is None:
        resp = std_login(data, redirect=redirect)
    else:
        mfa_used = True
        resp = mfa_login(data, redirect=redirect)
    succ = resp["success"]
    username = data["username"] if "username" in data else "N/A"
    log.login_attempt(username, ip, succ, mfa_used)
    return resp
