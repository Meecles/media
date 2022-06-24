
from flask import Blueprint, redirect, render_template

from auth.user_manager import get_auth_user
from utils.db_config import db

mod = Blueprint('view_manage_video', __name__)


def get_roles():
    available_roles = []
    roles = db["permissions"].find({"type": "role"})
    for item in roles:
        protected = "protected" in item and item["protected"]
        if not protected:
            available_roles.append(item["_id"])
    return available_roles


@mod.route("/manage/video")
def manage_videos():
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    details = user.get_details()
    if not user.has_any_permission(["access.settings"]):
        if "other" in details:
            oth = details["other"]
            if "ui_version" in oth and oth["ui_version"] == 2:
                return render_template("v2/defaults/404.html", info=info)
        return render_template("errors/404.html")
    return render_template("v2/manage/manage_videos.html", info=info, roles=get_roles())


@mod.route("/manage/video/show/<show_id>")
def manage_show(show_id):
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    details = user.get_details()
    not_found = "errors/404.html"
    if "other" in details:
        oth = details["other"]
        if "ui_version" in oth and oth["ui_version"] == 2:
            not_found = "v2/defaults/404.html"
    if not user.has_any_permission(["access.settings"]):
        return render_template(not_found, info=info)

    show = db["shows"].find_one({"_id": show_id})
    if show is None:
        return render_template(not_found, info=info)

    return render_template("v2/manage/manage_show.html", info=info, roles=get_roles(), show=show)


@mod.route("/manage/video/show/<show_id>/<season_id>")
def manage_season(show_id, season_id):
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    details = user.get_details()
    not_found = "errors/404.html"
    if "other" in details:
        oth = details["other"]
        if "ui_version" in oth and oth["ui_version"] == 2:
            not_found = "v2/defaults/404.html"
    if not user.has_any_permission(["access.settings"]):
        return render_template(not_found, info=info)

    show = db["shows"].find_one({"_id": show_id})
    if show is None:
        return render_template(not_found, info=info)

    if season_id not in show["seasons"]:
        return render_template(not_found, info=info)
    season = show["seasons"][season_id]
    season["id"] = season_id

    return render_template("v2/manage/manage_season.html", info=info, roles=get_roles(), show=show, season=season)
