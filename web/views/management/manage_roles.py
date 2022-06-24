from flask import Blueprint, redirect, render_template

from auth.user_manager import get_auth_user
from utils.db_config import db

mod = Blueprint('view_manage_roles', __name__)


def get_roles():
    available_roles = []
    roles = db["permissions"].find({"type": "role"})
    for item in roles:
        protected = "protected" in item and item["protected"]
        if not protected:
            available_roles.append(item["_id"])
    return available_roles


@mod.route("/manage/roles")
def manage_roles():
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    details = user.get_details()
    if not user.has_any_permission(["access.settings"]):
        if "other" in details:
            oth = details["other"]
            if "ui_version" in oth and oth["ui_version"] == 2:
                return render_template("v2/defaults/404.html", info=info)
        return render_template("errors/404.html")
    return render_template("v2/manage/manage_roles.html", info=info, roles=get_roles())
