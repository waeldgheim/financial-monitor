from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from os import getenv

SECRET_KEY = getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_crypt.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_crypt.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)