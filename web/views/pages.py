from flask import Blueprint, render_template, session, redirect, request

from auth import user_manager
from auth.user_manager import get_session_user, get_auth_user
from utils import themes
from utils.db_config import db

mod = Blueprint('view_pages', __name__)


def theme():
    return themes.get_theme(None)


def get_roles():
    available_roles = []
    roles = db["permissions"].find({"type": "role"})
    for item in roles:
        protected = "protected" in item and item["protected"]
        if not protected:
            available_roles.append(item["_id"])
    return available_roles


@mod.route('/', methods=['GET'])
def home_page():
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    details = user.get_details()
    if not user.has_permission("access.home"):
        if "other" in details:
            oth = details["other"]
            if "ui_version" in oth and oth["ui_version"] == 2:
                return render_template("v2/defaults/404.html", info=info)
        return render_template("errors/404.html")
    if "other" in details:
        oth = details["other"]
        if "ui_version" in oth and oth["ui_version"] == 2:
            homescreen = user.get_homescreen()
            redir = "/shows" if homescreen == "tv" else "/movies"
            return redirect(redir)
    return redirect("/videos")


@mod.route('/test', methods=['GET'])
def test():
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    #return render_template("v2/test.html", info=info)
    return redirect("/profile")


@mod.route('/videos', methods=['GET'])
def videos_page():
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    if not user.has_any_permission(["access.videos", "access.movies", "access.shows", "access.youtube"]):
        return render_template("errors/404.html")
    details = user.get_details()
    if "other" in details:
        oth = details["other"]
        if "ui_version" in oth and oth["ui_version"] == 2:
            homescreen = user.get_homescreen()
            redir = "/shows" if homescreen == "tv" else "/movies"
            return redirect(redir)
    return render_template("authenticated/video/videos_home.html", info=info, theme=theme())


@mod.route('/logout', methods=['GET'])
def cookie_monster():
    user = get_session_user()
    if user is not None:
        user_manager.remove_user(user)
    if "token" in session:
        session.pop('token')
    return redirect("/login?logout=true")


@mod.route('/login', methods=['GET'])
def login():
    if "token" in session:
        token = session.get("token")
        user = user_manager.get_user_no_auth(token)
        if user is None:
            session.pop("token")
            return redirect("/login")
        return redirect("/logout")
    logout = request.args.get("logout") is not None and request.args.get("logout") == "true"
    redir = "/"
    if request.args.get("redir") is not None:
        redir = request.args.get("redir")
    return render_template('v2/defaults/login.html', logout=logout, redir=redir)
