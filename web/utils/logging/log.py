import uuid
from datetime import timedelta
from threading import Thread

from utils.db_config import db
from utils.time_utils import get_current_datetime, to_date, to_string


class InsertThread(Thread):

    def __init__(self, collection, item):
        self.collection = collection
        self.item = item
        Thread.__init__(self)

    def run(self) -> None:
        db[self.collection].insert_one(self.item)


class MetricThread(Thread):

    def __init__(self, user_id, content_id, content_type):
        self.content_id = content_id
        self.content_type = content_type
        self.user_id = user_id
        self.now = get_current_datetime()
        Thread.__init__(self)

    def run(self) -> None:
        adjusted_time = to_date(self.now) - timedelta(minutes=90)
        metric = db["metrics"].find_one({
            "user_id": self.user_id,
            "type": self.content_type,
            "content_id": self.content_id,
            "time": {
                "$gt": to_string(adjusted_time)
            }
        }, ["_id", "time"])
        if metric is not None:
            db["metrics"].find_one_and_update({"_id": metric["_id"]}, {"$set": {"time": self.now}})
            return
        db["metrics"].insert_one({
            "_id": str(uuid.uuid4()),
            "user_id": self.user_id,
            "type": self.content_type,
            "content_id": self.content_id,
            "time": self.now
        })


def login_attempt(username, ip, success, mfa_used):
    now = get_current_datetime()
    InsertThread("logs", {
        "_id": str(uuid.uuid4()),
        "type": "login",
        "username": username,
        "ip": ip,
        "success": success,
        "mfa_used": mfa_used,
        "time": now
    }).start()


def watch_movie(user_id, movie_id):
    now = get_current_datetime()
    InsertThread("logs", {
        "_id": str(uuid.uuid4()),
        "type": "watch",
        "video_type": "movie",
        "user_id": user_id,
        "idv": movie_id,
        "time": now
    }).start()
    MetricThread(user_id, movie_id, "movie").start()


def watch_show(user_id, show_id):
    now = get_current_datetime()
    InsertThread("logs", {
        "_id": str(uuid.uuid4()),
        "type": "watch",
        "video_type": "tv_show",
        "user_id": user_id,
        "idv": show_id,
        "time": now
    }).start()
    MetricThread(user_id, show_id, "show").start()
