from flask import Blueprint, render_template, redirect

from auth.user_manager import get_auth_user
from utils import themes

mod = Blueprint('view_profile', __name__)


def theme():
    return themes.get_theme(None)


@mod.route('/profile', methods=['GET'])
def profile_page():
    user = get_auth_user()
    if user is None:
        return redirect("/login")
    info = user.get_info()
    if not user.has_any_permission(["access.profile"]):
        return render_template("errors/404.html")
    details = user.get_details()
    if "other" in details:
        oth = details["other"]
        if "ui_version" in oth and oth["ui_version"] == 2:
            return render_template("v2/defaults/profile.html", info=info, theme=theme())
    return render_template("authenticated/profile.html", info=info, theme=theme())
