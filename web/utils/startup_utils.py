from utils import default_perms
from utils.db_config import db

default_roles = default_perms.default_roles


def create_defaults(verbose=False):
    overwrite_defaults = False
    perms = db["permissions"]
    protected_admin = perms.find_one({"_id": "protected_admin"})
    if protected_admin is None or overwrite_defaults:
        if verbose:
            if overwrite_defaults:
                print("Protected admin found, but overwriting defaults")
            else:
                print("No protected admin found... creating")
        for role in default_roles:
            role_id = role["_id"]
            existing = perms.find_one({"_id": role_id})
            if existing is None:
                perms.insert_one(role)
            else:
                if overwrite_defaults:
                    perms.find_one_and_replace({"_id": role_id}, role)
    permissions = perms.find({"type": "permission"})
    if permissions is None:
        if verbose:
            print("No permissions document found... writing defaults")
        perms.insert_one(default_perms.default_perms)
    else:
        perm_list = []
        for perm in permissions:
            perm_list.append(perm)
        if len(perm_list) < 1:
            if verbose:
                print("No permissions document found... writing defaults")
            perms.insert_one(default_perms.default_perms)
        else:
            if verbose:
                print("Found permissions: ")
                for perm in permissions:
                    print(perm)
    video_settings = db["config"].find_one({"_id": "video_settings"})
    if video_settings is None:
        if verbose:
            print("No config for video settings found... writing defaults")
        db["config"].insert_one({
            "_id": "video_settings",
            "default_thumbnail": "default.png",
            "video_thumbs_volume": "/suite/thumbs",
            "video_movies_volume_h264": "/suite/movies",
            "video_shows_volume": "/suite/shows",
            "default_movie_title_position": "above"
        })
