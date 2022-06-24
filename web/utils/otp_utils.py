import pyotp


def generate_secret():
    return str(pyotp.random_base32())


def verify_token(secret, token):
    totp = pyotp.TOTP(secret)
    return totp.verify(token)


def get_provisioning_uri(secret, email):
    return pyotp.totp.TOTP(secret).provisioning_uri(email, issuer_name="Media Suite")
