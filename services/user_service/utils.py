from passlib.context import CryptContext

pwd_crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_crypt.hash(password)