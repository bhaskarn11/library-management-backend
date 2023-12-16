import secrets
from datetime import datetime, timedelta
import string
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.config import settings

digit = string.digits

pwd_context = CryptContext(schemes="bcrypt", deprecated="auto")


def generate_otp():
    otp = ''
    for i in range(6):
        otp += "".join(secrets.choice(digit))
        # print(otp)
    return otp


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password_hash(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt
