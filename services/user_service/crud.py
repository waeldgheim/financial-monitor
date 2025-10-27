from sqlalchemy.orm import Session
from models import User, RefreshToken
from utils import hash_password, verify_password
from datetime import datetime

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

def store_refresh_token(db: Session, user_id: int, jti: str, token_hash: str, expires_at: datetime):
    rt = RefreshToken(user_id=user_id, jti=jti, token_hash=token_hash, expires_at=expires_at)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt

def get_refresh_token_by_jti(db: Session, jti: str):
    return db.query(RefreshToken).filter(RefreshToken.jti == jti).first()

def revoke_refresh_token(db: Session, jti: str):
    row = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if row:
        db.delete(row)
        db.commit()
        return True
    return False

def revoke_all_refresh_tokens_for_user(db: Session, user_id: int):
    rows = db.query(RefreshToken).filter(RefreshToken.user_id == user_id).all()
    for r in rows:
        db.delete(r)
    db.commit()