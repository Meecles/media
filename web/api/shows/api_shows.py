from flask import Blueprint

from auth.user_manager import get_auth_user
from utils.db_config import db

mod = Blueprint('api_shows', __name__)
denied = {"success": False}


@mod.route("/api/shows/<show_id>/episodes/<season_id>")
def get_s_episodes(show_id, season_id):
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["access.videos", "access.shows"]):
        return denied

    show = db["shows"].find_one({"_id": show_id})
    if show is None:
        return {"success": False, "reason": "This show doesn't exist"}

    db_episodes = db["show_episodes"].find({"show_id": show_id, "season_id": season_id})
    episodes = []
    for episode in db_episodes:
        episodes.append(episode)

    return {"success": True, "episodes": episodes}


@mod.route("/api/shows/<show_id>/episodes")
def get_episodes(show_id):
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["access.videos", "access.shows"]):
        return denied

    show = db["shows"].find_one({"_id": show_id})
    if show is None:
        return {"success": False, "reason": "This show doesn't exist"}

    db_episodes = db["show_episodes"].find({"show_id": show_id})
    episodes = []
    for episode in db_episodes:
        episodes.append(episode)

    return {"success": True, "episodes": episodes}
