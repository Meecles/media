from flask import session

from auth.media_user import User

users = []


def get_session_user():
    if "token" in session:
        token = session.get("token")
        user = get_user(token)
        return user
    return None


def get_auth_user():
    if "token" in session:
        token = session.get("token")
        user = get_user(token)
        if user is not None and user.token == token and user.fully_authed:
            return user
    return None


def get_user(token):
    for user in users:
        if user.token == token:
            return user
    return None


def get_user_no_auth(token):
    for user in users:
        if user.token == token:
            return user
    return None


def add_user(user):
    users.append(user)


def remove_user(user):
    users.remove(user)


