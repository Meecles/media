import os
import uuid
from datetime import datetime

from utils import time_utils
from utils.db_config import db


class User:

    def __init__(self, username, token, uid, details):
        self.details = details
        self.username = username
        self.token = token
        self.uid = uid
        self.home_screen = None
        self.pending_secret = None
        self.fully_authed = False

    def refresh_user(self):
        pass

    def set_new_homescreen(self, screen):
        if screen in ["tv", "movie"]:
            self.home_screen = screen
            item = db["users"].find_one({"_id": self.get_uid()})
            item["home_screen"] = screen
            db["users"].find_one_and_replace({"_id": self.get_uid()}, item)

    def get_homescreen(self):
        if self.home_screen is not None:
            return self.home_screen
        item = db["users"].find_one({"_id": self.get_uid()}, ["home_screen"])
        return item["home_screen"] if "home_screen" in item else None

    def get_info(self):
        if self.is_fully_authed():
            mfa_paused = False
            mfa_pause_time = "N/A"
            other = self.details["other"]
            if "mfa-paused" in other:
                dbt = other["mfa-paused"]
                try:
                    t = datetime.strptime(dbt, time_utils.get_date_format())
                    now = datetime.strptime(time_utils.get_current_datetime(), time_utils.get_date_format())
                    if now <= t:
                        mfa_paused = True
                        mfa_pause_time = dbt
                except:
                    pass
            ret = {
                "logged_in": True,
                "username": self.get_username(),
                "mfa_enabled": self.mfa_enabled(),
                "roles": self.details["roles"],
                "perms": self.details["permissions"]
            }
            if mfa_paused:
                ret["mfa_paused"] = True
                ret["mfa_pause_time"] = mfa_pause_time
            return ret
        return {
            "logged_in": False
        }

    def has_movie_access(self, movie_id):
        if "all" in self.details["video_groups"]:
            return True
        ors = []
        for group in self.details["video_groups"]:
            ors.append({
                "_id": group
            })
        groups = db["video_groups"].find({"$or": ors})
        for group in groups:
            if "movies" in group:
                movies = group["movies"]
                if movie_id in movies:
                    return True
        return False

    def has_show_access(self, show_id, ep_id=None, idv=None, season_id=None):
        if "all" in self.details["video_groups"]:
            return True
        ors = []
        for group in self.details["video_groups"]:
            ors.append({
                "_id": group
            })
        groups = db["video_groups"].find({"$or": ors})
        for group in groups:
            if "shows" in group:
                shows = group["shows"]
                if show_id in shows:
                    if ep_id is None and idv is None and season_id is None:
                        return True
                    # add else for Future for episode or season based permissions
        return False

    def has_permission(self, permission):
        perms = self.details["permissions"]
        if "REGISTERPERMS" in os.environ:
            reg = os.environ["REGISTERPERMS"]
            if reg == "yes":
                req = db["debug"].find_one({"type": "perm_reg", "perm": permission})
                if req is None:
                    db["debug"].insert_one(
                        {
                            "_id": str(uuid.uuid4()),
                            "type": "perm_reg",
                            "perm": permission,
                            "user": self.username
                        }
                    )
        if "*" in perms:
            return True
        if permission in perms:
            return True
        for perm in perms:
            if perm.endswith("*") and permission.startswith(perm.replace("*", "")):
                return True
        return False

    def has_any_permission(self, permissions):
        for permission in permissions:
            if self.has_permission(permission):
                return True
        return False

    def get_details(self):
        return self.details

    def is_fully_authed(self):
        return self.fully_authed

    def set_fully_authed(self, fully_authed, ip=None):
        self.fully_authed = fully_authed
        if fully_authed and ip is not None:
            db["users"].find_one_and_update({"_id": self.uid}, {"$set": {"last_login_ip": ip}})

    def get_pending_secret(self):
        return self.pending_secret

    def pending_mfa(self, mfa_token):
        self.pending_secret = mfa_token

    def mfa_enabled(self):
        return self.details["mfa_enabled"]

    def get_uid(self):
        return self.uid

    def get_id(self):
        return self.get_uid()

    def get_username(self):
        return self.username
