from flask import Blueprint, render_template, redirect

from auth.user_manager import get_auth_user
from utils import themes
from utils.db_config import db

mod = Blueprint('view_legacy_pages', __name__)


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


@mod.route("/settings/logs")
def settings_logs():
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    if not user.has_any_permission(["access.settings"]):
        return render_template("errors/404.html")
    roles = get_roles()
    perm_doc = db["permissions"].find_one({"_id": "Default_Permissions", "type": "permission"})
    return render_template("authenticated/settings/settings_logs.html", info=info, roles=roles, theme=theme(),
                           permissions=perm_doc["permissions"])


@mod.route("/settings/roles")
def settings_roles():
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    if not user.has_any_permission(["access.settings"]):
        return render_template("errors/404.html")
    roles = get_roles()
    perm_doc = db["permissions"].find_one({"_id": "Default_Permissions", "type": "permission"})
    return render_template("authenticated/settings/settings_roles.html", info=info, roles=roles, theme=theme(),
                           permissions=perm_doc["permissions"])


@mod.route('/settings', methods=['GET'])
def settings_page():
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    if not user.has_any_permission(["access.settings"]):
        return render_template("errors/404.html")
    return render_template("authenticated/settings/settings_home.html", info=info, theme=theme())


@mod.route('/settings/users', methods=['GET'])
def settings_users_page():
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    if not user.has_any_permission(["access.settings"]):
        return render_template("errors/404.html")
    return render_template("authenticated/settings/settings_users.html", info=info, roles=get_roles(), theme=theme())


@mod.route('/settings/videos/show/<show_id>/<season_id>')
def settings_edit_episodes(show_id, season_id):
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    if not user.has_any_permission(["access.settings", "shows.edit"]):
        return render_template("errors/404.html")

    show = db["shows"].find_one({"_id": show_id})
    if show is None:
        return render_template("errors/404.html")

    if season_id not in show["seasons"]:
        return render_template("errors/404.html", back_link="/settings/videos/show/{}".format(show_id))
    season = show["seasons"][season_id]
    season["id"] = season_id
    return render_template("authenticated/settings/edit_episodes.html", info=info, show=show,
                           season=season, theme=theme())


@mod.route('/settings/videos/show/<show_id>')
def settings_edit_show(show_id):
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    if not user.has_any_permission(["access.settings", "shows.edit"]):
        return render_template("errors/404.html")

    show = db["shows"].find_one({"_id": show_id})
    if show is None:
        return render_template("errors/404.html")

    return render_template("authenticated/settings/edit_show_season.html", info=info, show=show, theme=theme())


@mod.route('/settings/videos', methods=['GET'])
def settings_videos_page():
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    if not user.has_any_permission(["access.settings", "shows.edit"]):
        return render_template("errors/404.html")
    return render_template("authenticated/settings/settings_videos.html", info=info, theme=theme())

