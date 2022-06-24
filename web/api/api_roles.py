
from flask import Blueprint, request

from auth.user_manager import get_auth_user
from utils.db_config import db

mod = Blueprint('api_roles', __name__)
denied = {"success": False}


@mod.route("/api/roles/export")
def export_roles():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_any_permission(["api.roles.export"]):
        return denied

    reset = request.args.get("reset")
    roles, video_groups = [], []

    if reset is None or not (reset == "both" or reset == "video_groups"):
        db_video_groups = db["video_groups"].find({})
        for group in db_video_groups:
            video_groups.append(group)
    if reset is None or not (reset == "both" or reset == "roles"):
        db_roles = db["permissions"].find({"type": "role"})
        for role in db_roles:
            roles.append(role)
    permissions = []
    default_perms = db["permissions"].find_one({"_id": "Default_Permissions", "type": "permission"})
    if default_perms is not None and "permissions" in default_perms:
        permissions = default_perms["permissions"]

    return {"success": True, "permissions": permissions, "video_groups": video_groups, "roles": roles}


@mod.route("/api/roles/<role_id>", methods=["DELETE"])
def delete_role(role_id):
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_any_permission(["api.roles.delete", "api.roles.edit"]):
        return denied

    role = db["permissions"].find_one({"_id": role_id, "type": "role"}, ["_id"])
    if role is None:
        return {"success": False, "reason": "Role with this name doesn't exist"}

    if "protected" in role and role["protected"]:
        return {"success": False, "reason": "This role is protected"}

    db_users = db["users"].find({"roles": role_id}, ["name"])
    users = [user["name"] for user in db_users]
    if len(users) > 0:
        return {"success": False, "reason": "Users with this role still exist", "users": users}

    db["permissions"].delete_one({"_id": role_id})

    return {"success": True}


@mod.route("/api/roles/add", methods=["POST"])
def roles_add():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_any_permission(["api.roles.add", "api.roles.edit"]):
        return denied
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except Exception as e:
        return {"success": False, "reason": "Invalid data"}

    req = ["id"]
    for item in req:
        if item not in data:
            return {"success": False, "reason": "Invalid data"}

    uid = data["id"]
    exists = db["permissions"].find_one({"_id": uid})
    if exists is not None:
        return {"success": False, "reason": "A role with that name already exists"}

    if not uid.isalnum():
        return {"success": False, "reason": "Role can only contain letters and numbers"}

    uid = uid.lower()

    permissions = data["permissions"] if "permissions" in data else []
    video_groups = data["video_groups"] if "video_groups" in data else []

    new_role = {
        "_id": uid,
        "type": "role",
        "permissions": permissions,
        "extra_roles": [],
        "video_groups": video_groups
    }

    db["permissions"].insert_one(new_role)

    return {"success": True}


@mod.route("/api/roles/edit", methods=["POST"])
def roles_edit():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_permission("api.roles.edit"):
        return denied
    data = {}
    try:
        data = request.get_json(force=True, silent=True)
    except Exception as e:
        return {"success": False, "reason": "Invalid data"}

    if "id" not in data or not isinstance(data["id"], str):
        return {"success": False, "reason": "Must provide a valid role ID"}

    role = db["permissions"].find_one({"_id": data["id"], "type": "role"})
    if role is None:
        return {"success": False, "reason": "This role does not exist"}

    if "protected" in role and role["protected"]:
        return {"success": False, "reason": "You can't modify protected roles"}

    updated = False
    if "video_groups" in data:
        video_groups = data["video_groups"]
        role["video_groups"] = video_groups
        updated = True

    if "permissions" in data:
        permissions = data["permissions"]
        role["permissions"] = permissions
        updated = True

    if updated:
        db["permissions"].find_one_and_replace({"_id": data["id"], "type": "role"}, role)

    return {"success": True}


def list_permissions():
    db_permissions = db["permissions"].find({"type": "permission"})
    perms = []
    added = []
    if db_permissions is None:
        return perms

    videos = db["video"].find({})
    show_ids = []
    movie_ids = []
    all_items = {}
    for vid in videos:
        tp = vid["type"]
        if tp == "movie":
            movie_ids.append(vid["_id"])
        if tp == "tv":
            show_ids.append(vid["_id"])
        all_items[vid["_id"]] = vid["name"]
    for db_perm in db_permissions:
        if "exact" in db_perm:
            exact = db_perm["exact"]
            for item in exact:
                if item["name"] not in added:
                    added.append(item["name"])
                    perms.append(item)
        if "template" in db_perm:
            for item in db_perm["template"]:
                prefix = item["prefix"]
                if prefix == "watch.show.":
                    for show_id in show_ids:
                        perms.append({
                            "name": prefix + show_id,
                            "description": "Watch TV Show: " + all_items[show_id],
                            "display_name": all_items[show_id],
                            "color": item["color"],
                            "special": True
                        })
                if prefix == "watch.movie.":
                    for movie_id in movie_ids:
                        perms.append({
                            "name": prefix + movie_id,
                            "description": "Watch movie: " + all_items[movie_id],
                            "display_name": all_items[movie_id],
                            "color": item["color"],
                            "special": True
                        })

    return perms


@mod.route("/api/roles/list", methods=["GET"])
def roles_list():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_permission("api.roles.list"):
        return denied

    db_roles = db["permissions"].find({"type": "role"})
    roles = []

    hide_protected = request.args.get("h")
    group_names = request.args.get("g")
    hide_protected = False if hide_protected is None else True if hide_protected == "y" else False
    group_names = False if group_names is None else True if group_names == "y" else False

    for role in db_roles:
        if "protected" not in role:
            role["protected"] = False
        if not hide_protected or not role["protected"]:
            if group_names:
                groups = []
                if "video_groups" in role:
                    groups = role["video_groups"]
                grps = []
                if len(groups) > 1:
                    ors = []
                    for group in groups:
                        ors.append({"_id": group})
                    db_groups = db["video_groups"].find({"$or": ors}, ["_id", "name"])
                    grps = [group for group in db_groups]
                elif len(groups) == 1:
                    group = db["video_groups"].find_one({"_id": groups[0]}, ["_id", "name"])
                    if group is not None:
                        grps.append(group)
                groups = {}
                for g in grps:
                    groups[g["_id"]] = g["name"]
                role["video_groups"] = groups
                roles.append(role)
            else:
                roles.append(role)

    return {"success": True, "roles": roles, "permissions": list_permissions()}


@mod.route("/api/permissions/list", methods=["GET"])
def permissions_list():
    user = get_auth_user()
    if user is None:
        return denied
    if not user.has_any_permission(["api.permissions.list", "api.roles.list"]):
        return denied

    perms = list_permissions()

    return {"success": True, "permissions": perms}


