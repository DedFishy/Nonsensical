import bcrypt
import secrets
import const

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(const.BCRYPT_SALT_ROUNDS))

def check_password(password: str, password_hash: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash)

def generate_token():
    return secrets.token_urlsafe(24)