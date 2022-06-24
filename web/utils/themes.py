import sys

from utils.db_config import db


def get_theme(theme=None):
    if "-debug" in sys.argv:
        theme = db["config"].find_one({"_id": "theme_trial"})
        if theme is not None:
            return theme["theme"]
    return {
        "h_tags": "#9fb3c8",
        "div": "#9fb3c8",
        "p": "#9fb3c8",
        "modal_background": "#486581",
        "body_background": "#243b53",
        "card": {
            "title": "#9fb3c8",
            "background": "#102a43"
        },
        "btn": {
            "danger": "#bf0031",
            "danger_text": "#fff",
            "outline_danger": "#bf0031",
            "primary": "#3039f9",
            "primary_text": "#fff",
            "outline_primary": "#3039f9",
            "info": "#00c7e6",
            "info_text": "#fff",
            "outline_info": "#00c7e6",
            "light": "#f8f9fa",
            "light_text": "#000",
            "outline_light": "#f8f9fa",
            "secondary": "#6c757d",
            "secondary_text": "#fff",
            "outline_secondary": "#6c757d",
            "success": "#36b37e",
            "success_text": "#fff",
            "outline_success": "#36b37e",
            "outline_success_hover": "#57d983"
        },
        "badge": {
            "primary": "#007bff",
            "primary_text": "#fff",
            "info": "#17a2b8",
            "info_text": "#fff",
            "danger": "#bf0031",
            "danger_text": "#fff"
        }
    }
