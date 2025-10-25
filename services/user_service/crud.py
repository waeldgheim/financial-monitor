from sqlalchemy.orm import Session
from models import User
from utils import hash_password, verify_password

def create_user(db: Session, username: str, email: str, password: str):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return None
    hashed_pw = hash_password(password)
    db_user = User(username=username, email=email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user