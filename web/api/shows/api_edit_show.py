import re
import uuid

from flask import Blueprint, request

from auth.user_manager import get_auth_user
from utils.db_config import db

mod = Blueprint('api_edit_shows', __name__)
denied = {"success": False}


@mod.route("/api/shows/<show_id>", methods=["POST"])
def edit_show(show_id):
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
    updated = False
    if "name" in data:
        name = data["name"]
        if name is not None and len(name) > 0:
            show["name"] = name
            updated = True
    if "base_path" in data:
        base_path = data["base_path"]
        comp_base_path = re.sub(r'[^a-zA-Z_0-9/]', '', base_path)
        if base_path == comp_base_path:
            show["base_path"] = base_path
            updated = True
    if "description" in data:
        description = data["description"]
        if description is not None and len(description) > 0:
            show["description"] = description
            updated = True
    if "thumb" in data:
        thumb = data["thumb"]
        if thumb is not None and len(thumb) > 0:
            show["thumb"] = thumb
            updated = True
    if updated:
        db["shows"].find_one_and_replace({"_id": show_id}, show)
    return {"success": True, "show": show}


@mod.route("/api/shows/<show_id>/<season_id>/edit_season", methods=["POST"])
def edit_season(show_id, season_id):
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
        return {"success": False, "reason": "Show does not exist"}

    if season_id not in show["seasons"]:
        return {"success": False, "reason": "season with this id doesn't exist for this show"}

    updated = False
    season_data = show["seasons"][season_id]
    for value in ["name", "alt_thumb", "base_path"]:
        if value in data:
            season_data[value] = data[value]
            updated = True
    if updated:
        show["seasons"][season_id] = season_data
        db["shows"].find_one_and_replace({"_id": show_id}, show)

    return {"success": True, "season_data": season_data}


@mod.route("/api/shows/<show_id>/add_season", methods=["POST"])
def add_season(show_id):
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
        return {"success": False, "reason": "Tv show with this ID does not exist"}

    if "name" not in data or "num" not in data:
        return {"success": False, "reason": "Invalid data"}

    num = data["num"]
    name = data["name"]

    try:
        num = int(num)
    except Exception as e:
        return {"success": False, "reason": "num must be a number"}

    new_key = "s{}".format(str(num))
    seasons = show["seasons"]
    if new_key in seasons:
        return {"success": False, "reason": "Season with this key already exists"}

    for key in seasons:
        season = seasons[key]
        if num == season["season"]:
            return {"success": False, "reason": "Season with this number already exists"}

    seasons[new_key] = {
        "season": num,
        "name": name,
        "alt_thumb": "N/A",
        "base_path": "N/A"
    }
    show["seasons"] = seasons
    db["shows"].find_one_and_replace({"_id": show_id}, show)

    return {"success": True}


@mod.route("/api/shows", methods=["PUT"])
def add_show():
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["shows.add"]):
        return denied
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except:
        return {"success": False, "reason": "Invalid data sent"}
    name, description, thumb, base_path = None, "N/A", "default.png", None
    if "name" in data:
        name = data["name"].strip()
    if name is None or len(name) < 1:
        return {"success": False, "reason": "Must provide a name"}
    if "description" in data:
        description = data["description"].strip()
        if len(description) < 1:
            description = "N/A"
    if "thumb" in data:
        thumb = data["thumb"].strip()
        if len(thumb) < 1:
            thumb = "default.png"
        if thumb.endswith(".mp4"):
            thumb = thumb.replace(".mp4", ".png")
    if "base_path" in data:
        base_path = data["base_path"]
    if base_path is None or len(base_path) < 1:
        base_path = name.replace(" ", "_").lower()
    base_path = re.sub(r'[^a-zA-Z_0-9/]', '', base_path)
    test = db["shows"].find_one({"name": name})
    if test is not None:
        return {"success": False, "reason": "A show with this name already exists"}
    item = {
        "_id": str(uuid.uuid4()),
        "name": name,
        "thumb": thumb,
        "base_path": base_path,
        "description": description,
        "seasons": {}
    }
    db["shows"].insert_one(item)
    return {"success": True}
