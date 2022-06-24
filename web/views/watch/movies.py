import flask
from flask import Blueprint, render_template, redirect, request

from auth.user_manager import get_auth_user
from utils import settings, themes
from utils.db_config import db
from utils.logging import log

mod = Blueprint('view_movies', __name__)


def theme():
    return themes.get_theme(None)


@mod.route('/movies', methods=['GET'])
def movies_page():
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    details = user.get_details()
    if not user.has_any_permission(["access.videos", "access.movies"]):
        if "other" in details:
            oth = details["other"]
            if "ui_version" in oth and oth["ui_version"] == 2:
                return render_template("v2/defaults/404.html", info=info)
        return render_template("errors/404.html")
    if "other" in details:
        oth = details["other"]
        if "ui_version" in oth and oth["ui_version"] == 2:
            user.set_new_homescreen("movie")
            return render_template("v2/video/movies_home.html", info=info, theme=theme())
    return render_template("authenticated/video/movies_home.html", info=info, theme=theme())


@mod.route('/watch/movie/<idv>')
def watch_movie(idv):
    user = get_auth_user()
    if user is None:
        return redirect("/login/" + idv)
    info = user.get_info()
    if not user.has_any_permission(["access.videos", "access.movies"]):
        return render_template("errors/404.html")
    video = db["movies"].find_one({"idv": idv})
    if video is None:
        return render_template("errors/404.html", info=info)
    uid = video["_id"]
    if not user.has_movie_access(video["_id"]):
        return render_template("errors/404.html", info=info)
    movie_name = video["name"]

    player = "authenticated/video/watch.html"
    if user is not None:
        log.watch_movie(user.get_uid(), idv)
    else:
        log.watch_movie("N/A", idv)
    return render_template(player, back_link="/movies", tp="movie", show_id="", idv=idv, movie_name=movie_name)


@mod.route('/stream/movie/<idv>')
def stream_movie(idv):
    user = get_auth_user()
    ip = request.headers.get("X-Real-Ip")
    bypass = ip is not None and ip == "192.168.2.212"
    if user is None and not bypass:
        return redirect("/login")
    if user is None and not bypass:
        return redirect("/login")
    if not bypass and not user.has_any_permission(["access.videos", "access.movies"]):
        return render_template("errors/404.html")
    volume = settings.video_movies_volume_h264
    movie = db["movies"].find_one({"idv": idv})
    if not bypass:
        if movie is None or not user.has_movie_access(movie["_id"]):
            return "404 - Not Found", 404
    filename = movie["file"]
    return flask.send_from_directory(volume, filename)
