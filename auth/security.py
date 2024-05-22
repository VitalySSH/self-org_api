import base64
from typing import Union

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def string_to_base64(s: str) -> bytes:
    return base64.b64encode(s.encode('utf-8'))


def base64_to_string(b: bytes) -> str:
    return base64.b64decode(b).decode('utf-8')


def hash_password(password: str) -> hash:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: hash) -> bool:
    return pwd_context.verify(password, hashed_password)


def encrypt_password(password: str) -> bytes:
    secret_password = ''.join(map(lambda x: chr(ord(x) ^ 127), password))
    return string_to_base64(secret_password)


def decrypt_password(secret_password: Union[str, bytes]) -> str:
    if isinstance(secret_password, str):
        secret_password = secret_password.encode('utf-8')
    password = base64_to_string(secret_password)
    return ''.join(map(lambda x: chr(ord(x) ^ 127), password))
