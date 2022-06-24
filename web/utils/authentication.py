import bcrypt

from utils.db_config import db


def find_user(email):
    collection = db["users"]
    return collection.find_one({"email": email})


def reset_pw(user_id, new_password, request_id=None):
    db_user = db["users"].find_one({"_id": user_id})
    if db_user is None:
        return {"success": False, "reason": "User ID not found"}
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(new_password.encode('utf8'), salt)
    hash_string = hashed.decode('utf8')
    db_user["password"] = hash_string
    db["users"].find_one_and_replace({"_id": user_id}, db_user)
    if request_id is not None:
        db["password_resets"].remove({"_id": request_id})
    return {"success": True}


def change_pw(user_id, existing, passwd):
    db_user = db["users"].find_one({"_id": user_id})
    if db_user is None:
        return {"success": False, "reason": "User ID not found"}
    hashed = db_user["password"]
    if bcrypt.checkpw(existing.encode('utf8'), hashed.encode('utf8')):
        salt = bcrypt.gensalt()
        nhashed = bcrypt.hashpw(passwd.encode('utf8'), salt)
        hash_string = nhashed.decode('utf8')
        db_user["password"] = hash_string
        db["users"].find_one_and_replace({"_id": user_id}, db_user)
        return {"success": True}
    return {"success": False, "reason": "The existing password is incorrect!"}
