import uuid

from flask import Blueprint, request

from auth.user_manager import get_auth_user
from utils import settings, generic_utils
from utils.db_config import db

mod = Blueprint('api_movies', __name__)
denied = {"success": False}


@mod.route("/api/movies")
def get_movies():
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["access.videos", "access.movies"]):
        return denied
    raw_req = request.args.get("raw")
    raw = raw_req is not None and raw_req == "true"
    if raw:
        if not user.has_any_permission(["api.video", "movies.edit"]):
            raw = False
    db_movies = db["movies"].find({})
    movies = []
    for db_movie in db_movies:
        uid = db_movie["_id"]
        if user.has_movie_access(uid):
            name, thumb, file, desc, categories, idv = "N/A", settings.default_thumb, db_movie["file"], \
                                                       "N/A", [], db_movie["idv"]
            if "thumb" in db_movie:
                if not raw:
                    if not db_movie["thumb"].startswith("thumbs/"):
                        thumb = "thumbs/" + db_movie["thumb"]
                    else:
                        thumb = db_movie["thumb"]
                else:
                    thumb = db_movie["thumb"]
            else:
                thumb = "N/A"
            if "name" in db_movie:
                name = db_movie["name"]
            if "description" in db_movie:
                desc = db_movie["description"]
            init_hide = "initial_hide" in db_movie and db_movie["initial_hide"]
            default_pos = settings.default_movie_title_position
            if default_pos is None:
                default_pos = "center"
            preview_position = db_movie["preview_position"] if "preview_position" in db_movie else default_pos
            item = {
                "_id": uid,
                "name": name,
                "thumb": thumb,
                "file": file,
                "description": desc,
                "categories": categories,
                "init_hide": init_hide,
                "preview_position": preview_position,
                "idv": idv
            }
            if "year" in db_movie:
                item["year"] = db_movie["year"]
            if "sort_priority" in db_movie:
                item["sort_priority"] = db_movie["sort_priority"]
            movies.append(item)
    return {"success": True, "movies": movies}


@mod.route("/api/movies", methods=["PUT"])
def add_movie():
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["movies.add"]):
        return denied
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except Exception as e:
        return {"success": False, "reason": "Invalid data sent"}
    name, description, thumb, file = None, "N/A", "default.png", None
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
    if "file" in data:
        file = data["file"].strip()
        replaces = [".png", ".mp3", ".mp5"]  # For typo's or mistakes
        for replace in replaces:
            if file.endswith(replace):
                file = file.replace(replace, ".mp4")
        if not file.endswith(".mp4"):
            file = "{}.mp4".format(file)
        if len(file) < 1:
            file = None
    if file is None:
        return {"success": False, "reason": "Must provide a file"}
    test_entry = db["movies"].find_one({"name": name})
    if test_entry is not None:
        return {"success": False, "reason": "Movie with this name already exists"}
    entry = {
        "_id": str(uuid.uuid4()),
        "idv": generic_utils.rand_str(12),
        "name": name,
        "thumb": thumb,
        "file": file,
        "description": description,
        "categories": []
    }
    db["movies"].insert_one(entry)
    return {"success": True}


@mod.route("/api/movies/<movie_id>", methods=["POST"])
def edit_movie(movie_id):
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["movies.edit"]):
        return denied
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except Exception as e:
        return {"success": False, "reason": "Invalid data sent"}
    movie = db["movies"].find_one({"_id": movie_id})
    if movie is None:
        return {"success": False, "reason": "Movie doesn't exist"}
    values = ["name", "thumb", "file", "description", "year"]
    updated = False
    for value in values:
        if value in data:
            if value == "year":
                raw = data[value].strip()
                try:
                    val = int(raw)
                    movie[value] = val
                    updated = True
                except:
                    if isinstance(raw, str):
                        if raw == "N/A" or len(raw) < 1:
                            movie.pop("year", None)
            else:
                val = data[value].strip()
                movie[value] = val
                updated = True
    if updated:
        db["movies"].find_one_and_replace({"_id": movie_id}, movie)
    return {"success": True}


@mod.route("/api/movies/<movie_id>", methods=["DELETE"])
def delete_movie(movie_id):
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["movies.edit"]):
        return denied

    movie = db["movies"].find_one({"_id": movie_id}, ["_id"])
    if movie is None:
        return {"success": False, "reason": "Movie does not exist"}

    db["movies"].delete_one({"_id": movie_id})

    return {"success": True}
