
def is_str_list(var):
    return all(isinstance(n, str) for n in var)


def is_str_list_old(var):
    if isinstance(var, list):
        for item in var:
            if not isinstance(item, str):
                return False
        return True
    return False


def username_valid(username):
    init_len = len(username)
    valid_chars = username.isalnum()
    if not valid_chars:
        return False
    return 2 < init_len < 17


def mfa_key_valid(mfa_key):
    try:
        x = int(mfa_key)
    except:
        return False
    return len(mfa_key) == 6
