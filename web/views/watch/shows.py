from pathlib import Path

import flask
from flask import Blueprint, render_template, redirect, request

from auth.user_manager import get_auth_user
from utils import settings, themes
from utils.db_config import db
from utils.logging import log

mod = Blueprint('view_shows', __name__)


def theme():
    return themes.get_theme(None)


@mod.route('/shows', methods=['GET'])
def shows_page():
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    details = user.get_details()
    if not user.has_any_permission(["access.videos", "access.shows"]):
        if "other" in details:
            oth = details["other"]
            if "ui_version" in oth and oth["ui_version"] == 2:
                return render_template("v2/defaults/404.html", info=info)
        return render_template("errors/404.html")
    if "other" in details:
        oth = details["other"]
        if "ui_version" in oth and oth["ui_version"] == 2:
            user.set_new_homescreen("tv")
            return render_template("v2/video/shows_home.html", info=info, theme=theme())
    return render_template("authenticated/video/shows_home.html", info=info, theme=theme())


@mod.route('/shows/<show_id>/<season_id>')
def season_page(show_id, season_id):
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    if not user.has_any_permission(["access.videos", "access.shows"]):
        return render_template("errors/404.html")
    if not user.has_show_access(show_id):
        return render_template("errors/404.html")
    show = db["shows"].find_one({"_id": show_id})
    if show is None:
        return render_template("errors/404.html")
    season_name = show["seasons"][season_id]["name"]
    dropdown = []
    for k in show["seasons"]:
        season = show["seasons"][k]
        active = season_id == k
        if active:
            active = "yes"
        else:
            active = "no"
        dropdown.append({
            "name": season["name"],
            "active": active,
            "id": k,
            "season": season["season"]
        })
    dropdown = sorted(dropdown, key=lambda ky: ky['season'])
    db_episodes = db["show_episodes"].find({"show_id": show_id, "season_id": season_id})
    episodes = []
    for episode in db_episodes:
        episodes.append(episode)
    episodes = sorted(episodes, key=lambda i: i['episode'])
    details = user.get_details()
    if "other" in details:
        oth = details["other"]
        if "ui_version" in oth and oth["ui_version"] == 2:
            return render_template("v2/video/shows_seasons.html", info=info, show=show, sid=season_id,
                           season_name=season_name, dd=dropdown, episodes=episodes, theme=theme())
    return render_template("authenticated/video/shows_seasons.html", info=info, show=show, sid=season_id,
                           season_name=season_name, dd=dropdown, episodes=episodes, theme=theme())


@mod.route('/shows/<show_id>')
def season_list_page(show_id):
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    if not user.has_any_permission(["access.videos", "access.shows"]):
        return render_template("errors/404.html")
    if not user.has_show_access(show_id):
        return render_template("errors/404.html")
    show = db["shows"].find_one({"_id": show_id})
    if show is None:
        return render_template("errors/404.html")
    if "seasons" not in show:
        return render_template("errors/404.html")
    seasons = show["seasons"]
    lowest_season, s_num = None, 0
    for key in seasons:
        season = seasons[key]
        num = season["season"]
        if lowest_season is None:
            lowest_season = key
            s_num = num
            continue
        if num < s_num:
            lowest_season = key
            s_num = num

    return redirect("/shows/{}/{}".format(show_id, lowest_season))


@mod.route('/watch/tv/<sid>/<idv>')
def watch_show(sid, idv):
    user = get_auth_user()
    if user is None:
        return redirect("/login" + idv)
    info = user.get_info()
    if not user.has_any_permission(["access.videos", "access.shows"]):
        return render_template("errors/404.html")
    episode = db["show_episodes"].find_one({"idv": idv})
    if episode is None or not user.has_show_access(episode["show_id"]):
        return render_template("errors/404.html")
    show = db["shows"].find_one({"_id": episode["show_id"]})
    if show is None:
        return render_template("errors/404.html")
    back_link = "/shows/{}/{}".format(episode["show_id"], sid)

    player = "authenticated/video/watch.html"
    if user is not None:
        log.watch_show(user.get_uid(), idv)
    else:
        log.watch_show("N/A", idv)
    return render_template(player, back_link=back_link, tp="tv", show_id=sid, idv=idv, episode=episode)


def is_file_valid(base_path, filename):
    fname = "{}/{}".format(base_path, filename)
    file = Path("{}/{}".format(settings.video_shows_volume, fname))
    if file.is_file():
        return True, fname
    return False, None


def is_dir_valid(p):
    volume = settings.video_shows_volume
    if not volume.endswith("/"):
        volume = "{}/".format(volume)
    loc = "{}{}".format(volume, p)
    file = Path(loc)
    valid = file.is_dir()
    return valid


def test_for_file(full_file_path, filename=None):
    if filename is not None and isinstance(filename, str):
        full_file_path = "{}/{}".format(full_file_path, filename)
    file = Path(full_file_path)
    return file.is_file()


def get_season_path(show, sid):
    if "seasons" not in show or sid not in show["seasons"]:
        return None
    season = show["seasons"][sid]
    base_path = season["base_path"] if "base_path" in season else None
    if base_path is not None:
        if base_path.lower() == "n/a" or base_path == "":
            base_path = None
    return base_path


def find_file_path(show, episode, sid):
    filename = episode["file"]
    volume = settings.video_shows_volume
    base_path = show["base_path"] if "base_path" in show else show["name"].lower().replace(" ", "_")
    if not is_dir_valid(base_path):
        print("Volume and base path not valid")
        return None

    season_path = get_season_path(show, sid)
    if season_path is None:
        full_path = "{}/{}".format(volume, base_path)
        if not full_path.startswith("/"):
            full_path = "/{}".format(full_path)
        if test_for_file(full_path, filename=filename):
            return full_path, filename
        full_path = "{}/{}/{}".format(volume, base_path, sid)
        if not full_path.startswith("/"):
            full_path = "/{}".format(full_path)
            return full_path, filename
        return None

    full_path = "{}/{}/{}".format(volume, base_path, season_path)
    if test_for_file(full_path, filename=filename):
        return full_path, filename
    full_path = "{}/{}".format(volume, base_path)
    if test_for_file(full_path, filename=filename):
        return full_path, filename

    full_path = "{}/{}/{}".format(volume, base_path, sid)
    if test_for_file(full_path, filename=filename):
        return full_path, filename

    return None


@mod.route('/stream/tv/<sid>/<idv>')
def stream_show(sid, idv):
    user = get_auth_user()
    ip = request.headers.get("X-Real-Ip")
    bypass = ip is not None and ip == "192.168.2.212"
    if user is None and not bypass:
        return redirect("/login")
    if user is None and not bypass:
        return redirect("/login")
    if not bypass and not user.has_any_permission(["access.videos", "access.shows"]):
        return "404 - Not Found", 404
    episode = db["show_episodes"].find_one({"idv": idv})
    if episode is None:
        return "404 - Not Found", 404
    if not bypass and not user.has_show_access(episode["show_id"]):
        return "404 - Not Found", 404
    show = db["shows"].find_one({"_id": episode["show_id"]})
    if show is None:
        return "404 - Not Found", 404

    result = find_file_path(show, episode, sid)
    if result is None:
        return "404 - Not Found", 404

    full_path, filename = result[0], result[1]

    return flask.send_from_directory(full_path, filename)



