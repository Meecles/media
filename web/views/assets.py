from pathlib import Path

import flask
from flask import Blueprint, render_template, redirect

from auth.user_manager import get_auth_user
from utils import settings

mod = Blueprint('view_assets', __name__)


@mod.route('/assets/<path:path>', methods=['GET'])
def assets(path):
    filename = path.split("/")[len(path.split("/")) - 1].replace(".", "_")
    # Default whitelist, but exceptions for these files
    # Technically no damage can be done if someone unauthorized has these since it's client side, but
    # it's cleaner to restrict access.
    restricted_assets = {
        "settings-video-groups_js": "settings.video_groups",
        "users_js": "access.settings",
        "edit-episode_js": "access.settings",
        "edit-show-season_js": "access.settings",
        "settings-movies_js": "access.settings",
        "settings-shows_js": "access.settings"
    }
    if filename not in restricted_assets:
        return flask.send_from_directory("static/assets", path)
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    if not user.has_permission(restricted_assets[filename]):
        return render_template("errors/404.html")
    return flask.send_from_directory("static/assets", path)


@mod.route('/thumbs/<path:path>')
def get_thumbs(path):
    test_file = Path("{}/{}".format(settings.video_thumbs_volume, path))
    if test_file.is_file():
        return flask.send_from_directory(settings.video_thumbs_volume, path)
    path = "thumbs/{}".format(path)
    test_file = Path("{}/{}".format(settings.video_thumbs_volume, path))
    if test_file.is_file():
        return flask.send_from_directory(settings.video_thumbs_volume, path)
    return flask.send_from_directory(settings.video_thumbs_volume, settings.default_thumb)
