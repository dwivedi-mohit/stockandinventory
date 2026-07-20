import hashlib
import os
import base64

SCRYPT_N = 16384
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 32


def hash_password(password):
    salt = os.urandom(16)
    if isinstance(password, str):
        password = password.encode("utf-8")
    key = hashlib.scrypt(password, salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=SCRYPT_DKLEN)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    key_b64 = base64.b64encode(key).decode("ascii")
    return f"$scrypt${SCRYPT_N}${salt_b64}${key_b64}"


def verify_password(password, stored):
    if not stored or not password:
        return False
    parts = stored.split("$")
    if len(parts) >= 5 and parts[1] == "scrypt":
        try:
            n = int(parts[2])
            salt = base64.b64decode(parts[3])
            expected = base64.b64decode(parts[4])
        except (IndexError, ValueError):
            return False
        if isinstance(password, str):
            password = password.encode("utf-8")
        computed = hashlib.scrypt(password, salt=salt, n=n, r=SCRYPT_R, p=SCRYPT_P, dklen=SCRYPT_DKLEN)
        return computed == expected
    return False
