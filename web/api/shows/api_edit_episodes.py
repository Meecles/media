import uuid

from flask import Blueprint, request

from auth.user_manager import get_auth_user
from utils import generic_utils
from utils.db_config import db

mod = Blueprint('api_edit_episodes', __name__)
denied = {"success": False}


def get_idv():
    length = 5
    idv = generic_utils.rand_str(length)
    check = db["show_episodes"].find_one({"idv": idv})
    i = 1
    while check is not None:
        if i % 2 == 0:
            length += 1
        idv = generic_utils.rand_str(length)
        check = db["show_episodes"].find_one({"idv": idv})
        i += 1
        if i > 30:
            return str(uuid.uuid4())
    return idv


@mod.route("/api/shows/<show_id>/<season_id>/<episode_id>", methods=["POST"])
def edit_episode(show_id, season_id, episode_id):
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["shows.edit"]):
        return denied
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except Exception as e:
        return {"success": False, "reason": "Invalid data sent"}
    show = db["shows"].find_one({"_id": show_id})
    if show is None:
        return {"success": False, "reason": "This show doesn't exist"}

    if season_id not in show["seasons"]:
        return {"success": False, "reason": "season with this id doesn't exist for this show"}

    episode = db["show_episodes"].find_one({"show_id": show_id, "season_id": season_id, "_id": episode_id})
    if episode is None:
        return {"success": False, "reason": "This episode doesn't exist"}

    if "name" in data:
        episode["name"] = data["name"]
    if "thumb" in data:
        episode["thumb"] = data["thumb"]
    if "file" in data:
        episode["file"] = data["file"]

    db["show_episodes"].find_one_and_replace({"_id": episode_id, "show_id": show_id}, episode)

    return {"success": True, "episode": episode}


@mod.route("/api/shows/<show_id>/<season_id>/add_episode", methods=["POST"])
def add_episode(show_id, season_id):
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["shows.edit"]):
        return denied
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except:
        return {"success": False, "reason": "Invalid data sent"}
    show = db["shows"].find_one({"_id": show_id})
    if show is None:
        return {"success": False, "reason": "This show doesn't exist"}

    if season_id not in show["seasons"]:
        return {"success": False, "reason": "season with this id doesn't exist for this show"}

    name, thumb, episode, file = None, None, 0, None
    if "name" not in data or "episode" not in data or "file" not in data:
        return {"success": False, "reason": "Not enough information"}

    try:
        episode = int(data["episode"])
    except:
        return {"success": False, "reason": "Episode must be a number"}

    exists = db["show_episodes"].find_one({"episode": episode, "show_id": show_id, "season_id": season_id})
    if exists is not None:
        return {"success": False, "reason": "This episode already exists"}

    name = data["name"]
    thumb = "N/A"
    if "thumb" in data:
        thumb = data["thumb"]
        if len(thumb) < 1:
            thumb = "N/A"
        else:
            if thumb.lower().endswith(".mp4"):
                thumb = thumb.replace(".mp4", ".png")

    file = data["file"]
    if not file.endswith(".mp4"):
        file = "{}.mp4".format(file)

    idv = get_idv()

    new_episode = {
        "_id": str(uuid.uuid4()),
        "idv": idv,
        "show_id": show_id,
        "season_id": season_id,
        "name": name,
        "thumb": thumb,
        "episode": episode,
        "file": file
    }
    db["show_episodes"].insert_one(new_episode)

    return {"success": True, "show": show}
