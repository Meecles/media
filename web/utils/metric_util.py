from utils.db_config import db


def get_movie_metrics(user_id):
    movies = db["metrics"].find({"user_id": user_id, "type": "movie"})
    counts = {}
    unique = {}
    for movie in movies:
        idv = movie["content_id"]
        counts[idv] = counts[idv] + 1 if idv in counts else 1
    idvs = [{"idv": idv} for idv in counts]
    if len(idvs) > 1:
        movie_names = db["movies"].find({"$or": idvs}, ["idv", "name"])
        for movie in movie_names:
            unique[movie["idv"]] = {
                "count": counts[movie["idv"]],
                "name": movie["name"]
            }
    elif len(idvs) == 1:
        movie = db["movies"].find_one(idvs[0], ["idv", "name"])
        if movie is not None:
            unique[movie["idv"]] = {
                "count": counts[movie["idv"]],
                "name": movie["name"]
            }
    return unique


def get_show_metrics(user_id):
    shows = db["metrics"].find({"user_id": user_id, "type": "show"})
    counts = {}
    for show in shows:
        idv = show["content_id"]
        counts[idv] = counts[idv] + 1 if idv in counts else 1
    idvs = [{"idv": idv} for idv in counts]

    episodes = []
    if len(idvs) > 1:
        episodes = [x for x in db["show_episodes"].find({"$or": idvs}, ["show_id", "name", "idv"])]
    elif len(idvs) == 1:
        ep = db["show_episodes"].find_one(idvs[0], ["idv", "show_id", "name"])
        if ep is not None:
            episodes = [ep]
    show_ids = []
    for episode in episodes:
        show_id = episode["show_id"]
        if show_id not in show_ids:
            show_ids.append(show_id)
    tv_shows = []
    show_map = {}
    if len(show_ids) > 1:
        tv_shows = [x for x in db["shows"].find({"$or": [{"_id": show_id} for show_id in show_ids]})]
    elif len(show_ids) == 1:
        show = db["shows"].find_one({"_id": show_ids[0]})
        if show is not None:
            tv_shows = [show]
    for show in tv_shows:
        show_map[show["_id"]] = show
    metrics = {}
    for episode in episodes:
        show_id = episode["show_id"]
        if show_id not in metrics:
            eps = {}
            eps[episode["idv"]] = {
                "name": episode["name"],
                "count": counts[episode["idv"]]
            }
            metrics[show_id] = {
                "total_views": counts[episode["idv"]],
                "name": show_map[show_id]["name"],
                "episodes": eps
            }
        else:
            item = metrics[show_id]
            eps = item["episodes"]
            eps[episode["idv"]] = {
                "name": episode["name"],
                "count": counts[episode["idv"]]
            }
            val = item["total_views"] + counts[episode["idv"]]
            item["total_views"] = val
            metrics[show_id] = item

    return metrics


