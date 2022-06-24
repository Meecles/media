import os
import uuid

import pymongo

from utils import generic_utils
from utils.db_config import db


class Database:

    def __init__(self, ip, port, database):
        self.ip = ip
        self.port = port
        self.database = database

    def get_db(self):
        mongo_ip = self.ip
        db_connect_string = "mongodb://{}:{}".format(mongo_ip, self.port)
        db_name = self.database
        print("Connecting to {}".format(db_connect_string))
        client = pymongo.MongoClient(db_connect_string)
        return client[db_name]


class Movie:

    def __init__(self, name, thumb, file):
        self.name = name
        self.thumb = thumb
        self.file = file
        self.convert()
        self.uid = str(uuid.uuid4())
        self.idv = generic_utils.rand_str(12)
        self.categories = []
        self.description = "N/A"

    def convert(self):
        self.thumb = self.thumb.replace("thumbs/", "")
        self.file = self.file.replace("videos/movies/", "")

    def get_json(self):
        return {
            "_id": self.uid,
            "name": self.name,
            "thumb": self.thumb,
            "file": self.file,
            "description": self.description,
            "categories": self.categories,
            "idv": self.idv
        }

    def get_name(self):
        return self.name

    def regenerate_ids(self):
        self.uid = str(uuid.uuid4())
        self.idv = generic_utils.rand_str(12)

    def name_exists(self):
        movie = db["movies"].find_one({"name": self.name})
        return movie is not None

    def ids_exists(self):
        movie = db["movies"].find_one({"$or": [
            {
                "_id": self.uid
            },
            {
                "idv": self.idv
            }
        ]})
        return movie is not None


class Show:

    def __init__(self, show_json):
        self.show_json = show_json
        self.name = show_json["name"]
        self.uid = str(uuid.uuid4())
        self.thumb = show_json["thumb"]
        self.base_path = self.name.replace(" ", "_").lower()
        self.description = "N/A"
        self.seasons = {}
        self.episodes = []
        self.convert()
        self.process_seasons()

    def convert(self):
        self.thumb = self.thumb.replace("thumbs/", "")

    def get_show_json(self):
        return {
            "_id": self.uid,
            "name": self.name,
            "thumb": self.thumb,
            "base_path": self.base_path,
            "description": self.description,
            "seasons": self.seasons
        }

    def get_episodes(self):
        return self.episodes

    def exists(self):
        show = db["shows"].find_one({"name": self.name})
        return show is not None

    def process_seasons(self):
        seasons = self.show_json["seasons"]
        for key in seasons:
            season = seasons[key]
            season_name = season["name"]
            season_base_path = "N/A"
            for ek in season["episodes"]:
                episode = season["episodes"][ek]
                ep_num = episode["episode"]
                idv = generic_utils.rand_str(20)
                thumb = episode["thumb"].replace("thumbs/", "")
                name = episode["name"]
                file = None
                pre_file = episode["file"].replace("videos/tv/", "")
                if "/" in pre_file:
                    file_p = pre_file.split("/")
                    if len(file_p) == 2:
                        self.base_path = file_p[0]
                        file = file_p[1]
                    elif len(file_p) == 3:
                        self.base_path = file_p[0]
                        season_base_path = file_p[1]
                        file = file_p[2]
                if file is not None:
                    self.episodes.append({
                        "_id": str(uuid.uuid4()),
                        "idv": idv,
                        "show_id": self.uid,
                        "season_id": key,
                        "name": name,
                        "thumb": thumb,
                        "episode": int(ep_num),
                        "file": file
                    })
            self.seasons[key] = {
                "season": int(key.replace("s", "")),
                "name": season_name,
                "alt_thumb": "N/A",
                "base_path": season_base_path
            }


def migrate_shows(simulate=True):
    print("Starting show migration")
    odb = Database("media_migrate", "27017", "mediaserver").get_db()
    print("DB Connected")
    o_shows = odb["video"].find({"type": "tv"})
    shows = []
    for show in o_shows:
        sh = Show(show)
        if not sh.exists():
            shows.append(sh)
    print("Found {} shows to insert".format(str(len(shows))))
    if simulate:
        print("Sample:")
        print(shows[0].get_show_json())
        print("\n")
        print(shows[0].get_episodes()[0])
        return
    if len(shows) == 1:
        show = shows[0]
        db["shows"].insert_one(show.get_show_json())
        db["show_episodes"].insert_many(show.get_episodes())
    elif len(shows) > 1:
        show_jsons = [show.get_show_json() for show in shows]
        db["shows"].insert_many(show_jsons)
        for show in shows:
            db["show_episodes"].insert_many(show.get_episodes())


def migrate_movies(simulate=True):
    print("Starting movie migration")
    odb = Database("media_migrate", "27017", "mediaserver").get_db()
    print("DB connected")
    o_movies = odb["video"].find({"type": "movie"})
    n_movies = []
    for m in o_movies:
        name = m["name"]
        thumb = m["thumb"]
        file = m["file"]
        movie = Movie(name, thumb, file)
        if not movie.name_exists():
            while movie.ids_exists():
                movie.regenerate_ids()
            n_movies.append(movie)
    movies = [movie.get_json() for movie in n_movies]
    print("Found {} movies to insert!".format(str(len(movies))))
    if simulate:
        print("Sample: ")
        print(movies[0])
        return
    if len(movies) > 1:
        db["movies"].insert_many(movies)
    elif len(movies) == 1:
        db["movies"].insert_one(movies[0])
    print("Inserted {} movies".format(str(len(movies))))

