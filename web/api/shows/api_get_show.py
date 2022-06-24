from flask import Blueprint, request

from auth.user_manager import get_auth_user
from utils.db_config import db

mod = Blueprint('api_get_shows', __name__)
denied = {"success": False}


@mod.route("/api/shows")
def get_shows():
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["access.videos", "access.shows"]):
        return denied
    raw_req = request.args.get("raw")
    raw = raw_req is not None and raw_req == "true"
    if raw:
        if not user.has_any_permission(["api.video", "shows.edit"]):
            raw = False
    show_filter = request.args.get("filter")
    search_doc = {}
    if show_filter is not None and isinstance(show_filter, str):
        search_doc = {"_id": show_filter}
    db_shows = db["shows"].find(search_doc)
    shows = []
    for show in db_shows:
        if user.has_show_access(show["_id"]):
            show_id, name, thumb, seasons = show["_id"], "N/A", "thumbs/default.png", 0
            if "name" in show:
                name = show["name"]
            if "thumb" in show:
                if not raw:
                    if not show["thumb"].startswith("thumbs/"):
                        thumb = "thumbs/" + show["thumb"]
                    else:
                        thumb = show["thumb"]
                else:
                    thumb = show["thumb"]
            season_data = {}
            if "seasons" in show:
                sns = show["seasons"]
                seasons = len(sns)
                season_data = sns
            description = "N/A"
            if "description" in show:
                if show["description"] is not None and len(show["description"]) > 0:
                    description = show["description"]
            if not raw:
                shows.append({
                    "_id": show_id,
                    "name": name,
                    "thumb": thumb,
                    "description": description,
                    "season_count": seasons
                })
            else:
                base_path = ""
                if "base_path" in show:
                    base_path = show["base_path"]
                reported_season_data = {}
                for key in season_data:
                    count = db["show_episodes"].find({
                        "show_id": show_id,
                        "season_id": key
                    }).count()
                    reported_season_data[key] = season_data[key]
                    reported_season_data[key]["episodes"] = count

                shows.append({
                    "_id": show_id,
                    "name": name,
                    "thumb": thumb,
                    "season_count": seasons,
                    "description": description,
                    "seasons": reported_season_data,
                    "base_path": base_path
                })
    return {"success": True, "shows": shows}

