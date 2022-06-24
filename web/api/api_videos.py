from flask import Blueprint

from auth.user_manager import get_auth_user
from utils.db_config import db

mod = Blueprint('api_videos', __name__)
denied = {"success": False}


@mod.route("/api/videos")
def get_videos():
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["settings.videos"]):
        return denied

    db_movies = db["movies"].find({}, ["_id", "name"])
    db_shows = db["shows"].find({}, ["_id", "name"])
    movies = [movie for movie in db_movies]
    shows = [show for show in db_shows]

    return {"success": True, "movies": movies, "shows": shows}
