import uuid

from flask import Blueprint, request

from auth.user_manager import get_auth_user
from utils.db_config import db

mod = Blueprint("api_video_groups", __name__)


@mod.route("/api/video_groups")
def get_video_groups():
    user = get_auth_user()
    if user is None:
        return {"success": False}
    info = user.get_info()
    if not user.has_any_permission(["access.videos", "access.movies", "access.shows"]):
        return {"success": False}
    db_groups = db["video_groups"].find({})
    translate = request.args.get("translate")
    if translate is not None and (translate == "movies" or translate == "shows" or translate == "both"):
        pass
    if translate is None:
        translate = ""
    groups = []
    for group in db_groups:
        if translate == "movies" or translate == "both":
            ors = []
            movie_names = {}
            if "movies" in group:
                movies = group["movies"]
                for movie in movies:
                    ors.append({"_id": movie})
                if len(ors) == 1:
                    db_movie = db["movies"].find_one(ors[0], ["_id", "name"])
                    if db_movie is not None:
                        movie_names[db_movie["_id"]] = db_movie["name"]
                elif len(ors) > 1:
                    db_movies = db["movies"].find({"$or": ors}, ["_id", "name"])
                    for movie in db_movies:
                        movie_names[movie["_id"]] = movie["name"]
            group["movie_names"] = movie_names
        if translate == "shows" or translate == "both":
            ors = []
            show_names = {}
            if "shows" in group:
                shows = group["shows"]
                for show in shows:
                    ors.append({"_id": show})
                if len(ors) == 1:
                    show = db["shows"].find_one(ors[0], ["_id", "name"])
                    if show is not None:
                        show_names[show["_id"]] = show["name"]
                elif len(ors) > 1:
                    db_shows = db["shows"].find({"$or": ors}, ["_id", "name"])
                    for show in db_shows:
                        show_names[show["_id"]] = show["name"]
            group["show_names"] = show_names
        groups.append(group)

    return {"success": True, "groups": groups}


@mod.route("/api/video_groups", methods=["POST"])
def add_group():
    user = get_auth_user()
    if user is None:
        return {"success": False}
    info = user.get_info()
    if not user.has_any_permission(["settings.video_groups"]):
        return {"success": False}
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except Exception as e:
        return {"success": False, "reason": "No data sent"}
    name = "New Group"
    movies = []
    shows = []
    if data is not None:
        if "name" in data:
            name = data["name"]
        if "shows" in data:
            shows = data["shows"]
        if "movies" in data:
            movies = data["movies"]
        if "movie" in data:
            movies.append(data["movie"])
        if "show" in data:
            shows.append(data["show"])
    group = {
        "_id": str(uuid.uuid4()),
        "name": name,
        "movies": movies,
        "shows": shows
    }
    db["video_groups"].insert_one(group)
    return {"success": True, "group": group}


@mod.route("/api/video_groups/<group_id>", methods=["DELETE"])
def delete_group(group_id):
    user = get_auth_user()
    if user is None:
        return {"success": False}
    info = user.get_info()
    if not user.has_any_permission(["settings.video_groups"]):
        return {"success": False}
    group = db["video_groups"].find_one({"_id": group_id})
    if group is not None:
        db_roles = db["permissions"].find({"video_groups": group_id}, ["_id"])
        roles = [role["_id"] for role in db_roles]
        if len(roles) > 0:
            role_str = ""
            if len(roles) <= 3:
                role_str = ", ".join(roles)
            else:
                role_str = "{} roles".format(str(len(roles)))
            return {"success": False, "reason": "This group is being used by the following roles: {}".format(role_str)}
        db["video_groups"].delete_one({"_id": group_id})
    return {"success": True}


@mod.route("/api/video_groups/<group_id>", methods=["PUT"])
def edit_group(group_id):
    user = get_auth_user()
    if user is None:
        return {"success": False}
    info = user.get_info()
    if not user.has_any_permission(["settings.video_groups"]):
        return {"success": False}

    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except Exception as e:
        return {"success": False, "reason": "No data sent"}

    group = db["video_groups"].find_one({"_id": group_id})
    if group is None:
        return {"success": False, "reason": "Group with this ID doesn't exist"}

    if "shows" in data:
        group["shows"] = [show for show in data["shows"]]
    if "movies" in data:
        group["movies"] = [movie for movie in data["movies"]]
    if "name" in data:
        group["name"] = data["name"]
    if "add_shows" in data:
        shows = [show for show in data["add_shows"]]
        for show in shows:
            if show not in group["shows"]:
                group["shows"].append(show)
    if "add_movies" in data:
        movies = [movie for movie in data["add_movies"]]
        for movie in movies:
            if movie not in group["movies"]:
                group["movies"].append(movie)

    db["video_groups"].find_one_and_replace({"_id": group_id}, group)

    return get_video_groups()
