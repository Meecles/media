import uuid

import bcrypt

from utils import generic_utils
from utils.db_config import db


def gen_pass():
    return generic_utils.rand_str(16)


def create_user(username, password, roles, require_mfa):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf8'), salt)
    hash_string = hashed.decode('utf8')

    user_doc = {
        "_id": str(uuid.uuid4()),
        "username": username,
        "name": username,
        "password": hash_string,
        "roles": roles,
        "mfa_required": require_mfa,
        "ui_version": 2
    }

    db["users"].insert_one(user_doc)


def create_default_user():
    query = {
        "$or": [
            {"roles": "admin"},
            {"roles": "protected_admin"}
        ]
    }
    accts = db["users"].find_one(query)
    if accts is None:
        require_mfa = True
        def_pass = gen_pass()
        def_user = "admin"
        overwrite = False
        db_admin_exists = db["users"].find_one({"username": "admin"})
        if db_admin_exists is not None:
            overwrite = True
            db["users"].delete_one({"username": "admin"})
        roles = ["protected_admin"]
        create_user(def_user, def_pass, roles, require_mfa)
        print("\n\n===== New Admin Account Created =====")
        if overwrite:
            print("WARNING: Overwrote account 'admin' as it did not have any admin privleges!\n")
        print("No admin account found! Created default account: \nUsername: " + def_user + "\nPassword: " + def_pass)
        print("Do not lose this password! Log in, enable MFA, and manage users from there.\n===== =====\n\n")
