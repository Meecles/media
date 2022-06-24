from flask import Blueprint

from auth.user_manager import get_auth_user
from utils import metric_util
from utils.db_config import db

mod = Blueprint('api_metrics', __name__)
denied = {"success": False}


@mod.route("/api/metrics/<user_id>/<metric>")
def my_metrics(user_id, metric):
    user = get_auth_user()
    if user is None:
        return denied
    info = user.get_info()
    if not user.has_any_permission(["metrics.top"]):
        return denied
    username = "N/A"
    if metric not in ["all", "movie", "movies", "show", "shows"]:
        return {"success": False, "reason": "Invalid metric"}
    if user_id == "my":
        user_id = user.get_id()
        username = user.get_username()
    else:
        if not user.has_any_permission(["metrics.other"]):
            return denied
        user_details = db["users"].find_one({"_id": user_id}, ["_id", "username"])
        if user_details is None:
            return {"success": False, "reason": "User not found"}
        username = user_details["username"]

    response = {"success": True, "username": username, "user_id": user_id}
    if metric == "movie" or metric == "movies":
        response["movie"] = metric_util.get_movie_metrics(user_id)
    if metric == "show" or metric == "shows":
        response["shows"] = metric_util.get_show_metrics(user_id)
    if metric == "all":
        response["shows"] = metric_util.get_show_metrics(user_id)
        response["movie"] = metric_util.get_movie_metrics(user_id)
    return response


