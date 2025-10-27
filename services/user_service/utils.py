from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from os import getenv
from uuid import uuid4
import hashlib

SECRET_KEY = getenv("JWT_SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_EXPIRE_DAYS = int(getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

pwd_crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_crypt.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_crypt.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    jti = str(uuid4())
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "jti": jti, "type": "refresh"})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, jti, token_hash, expire

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None