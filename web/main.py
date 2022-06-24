import os
import sys
import uuid

from flask import render_template, Flask, redirect
from flask_wtf import CsrfProtect

from api import api_login, api_roles, api_user_utils, api_movies, api_user, api_video_groups, api_videos
from api.logging import metrics, fetch_logs
from api.shows import api_get_show, api_edit_show, api_shows, api_edit_episodes
from auth import profile_utils
from auth.user_manager import get_auth_user
from utils import user_utils, startup_utils, settings, migrate
from utils.db_config import db
from views import pages, assets, profile
from views.management import manage, manage_user, manage_video, manage_roles, manage_groups
from views.legacy import legacy_pages
from views.watch import shows, movies

app = Flask(__name__)


def get_secret_key():
    secrets = db["config"].find_one({"_id": "secrets"})
    if secrets is None:
        secrets = {
            "_id": "secrets",
            "app_secret_key": str(uuid.uuid4())
        }
        db["config"].insert_one(secrets)
    return secrets["app_secret_key"]


app.secret_key = get_secret_key()

migrated = False

registers = [
    pages.mod,
    legacy_pages.mod,
    movies.mod,
    shows.mod,
    profile.mod,
    profile_utils.mod,
    api_login.mod,
    api_roles.mod,
    api_movies.mod,
    api_shows.mod,
    api_get_show.mod,
    api_edit_episodes.mod,
    api_edit_show.mod,
    api_user.mod,
    api_videos.mod,
    api_video_groups.mod,
    api_user_utils.mod,
    assets.mod,
    metrics.mod,
    fetch_logs.mod,
    manage.mod,
    manage_user.mod,
    manage_video.mod,
    manage_roles.mod,
    manage_groups.mod
]

for registration in registers:
    app.register_blueprint(registration)

CsrfProtect(app)

if "REGISTERPERMS" in os.environ:
    reg = os.environ["REGISTERPERMS"]
    if reg == "yes":
        print("Debug permission registration is enabled!")


@app.errorhandler(404)
def page_not_found(e):
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    details = user.get_details()
    if "other" in details:
        oth = details["other"]
        if "ui_version" in oth and oth["ui_version"] == 2:
            return render_template("v2/defaults/404.html", info=info)
    return render_template("errors/404.html", info=info)


def get_env(value):
    return os.environ[value] if value in os.environ and os.environ[value] is not None else None


def load_settings():
    conf = db["config"].find_one({"_id": "video_settings"})
    if conf is None:
        print("Error loading config.")
        quit()
    settings.default_thumb = conf["default_thumbnail"]
    settings.video_thumbs_volume = conf["video_thumbs_volume"]
    settings.video_movies_volume_h264 = conf["video_movies_volume_h264"]
    settings.video_shows_volume = conf["video_shows_volume"]
    settings.default_movie_title_position = conf["default_movie_title_position"] \
        if "default_movie_title_position" in conf else None


def update_script():
    users = db["users"].find({})
    for user in users:
        if "ui_version" not in user:
            user["ui_version"] = 2
            db["users"].find_one_and_replace({"_id": user["_id"]}, user)


if __name__ == '__main__':
    startup_utils.create_defaults()
    load_settings()
    update_script()
    user_utils.create_default_user()
    debug = False
    if "-debug" in sys.argv or "DEBUG" in os.environ:
        if os.environ["DEBUG"] is not None:
            if os.environ["DEBUG"].lower() == "true":
                debug = True

    if "-migrate" in sys.argv and not migrated:
        sim = False
        migrate.migrate_movies(simulate=sim)
        migrate.migrate_shows(simulate=sim)
        migrated = True
    else:
        if "MIGRATE" in os.environ:
            if os.environ["MIGRATE"] == "movies" or os.environ["MIGRATE"] == "both":
                migrate.migrate_movies(simulate=False)
            if os.environ["MIGRATE"] == "shows" or os.environ["MIGRATE"] == "both":
                migrate.migrate_shows(simulate=False)
    mongo_reload = False
    host = get_env("WEB_HOST") or "127.0.0.1"
    if host == "all":
        host = "0.0.0.0"

    print("Starting Web portal...")
    app.run(debug=debug, port=8080, host=host)
