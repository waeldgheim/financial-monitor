from fastapi import APIRouter, Depends, status, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from shared_lib.db import SessionLocal
from models import User
from crud import create_user, authenticate_user, store_refresh_token, get_refresh_token_by_jti, revoke_refresh_token
from schemas import UserCreate, TokenResponse, LoginRequest, UserProfile, RefreshRequest
from utils import create_access_token, verify_token, create_refresh_token
from datetime import timedelta
import hashlib
from datetime import datetime

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user

@router.get("/users")
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, username=user.username, email=user.email, password=user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    access_token_expires = timedelta(minutes=60)
    access_token  = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token, jti, token_hash, expires_at = create_refresh_token({"sub": user.email})
    store_refresh_token(db, user_id=user.id, jti=jti, token_hash=token_hash, expires_at=expires_at)
    return {
    "access_token": access_token,
    "token_type": "bearer",
    "refresh_token": refresh_token
    }

@router.post("/login", response_model=TokenResponse)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, email=request.email, password=request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        ) 
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token, jti, token_hash, expires_at = create_refresh_token({"sub": user.email})
    store_refresh_token(db, user_id=user.id, jti=jti, token_hash=token_hash, expires_at=expires_at)
    return {
    "access_token": access_token,
    "token_type": "bearer",
    "refresh_token": refresh_token
    }

@router.get("/profile", response_model=UserProfile)
def read_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/token/refresh", response_model=TokenResponse)
def refresh_token_endpoint(refresh_token: RefreshRequest, db: Session = Depends(get_db)):
    payload = verify_token(refresh_token.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    jti = payload.get("jti")
    db_row = get_refresh_token_by_jti(db, jti)
    if not db_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked or not found")

    if db_row.token_hash != hashlib.sha256(refresh_token.refresh_token.encode()).hexdigest():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if db_row.expires_at < datetime.utcnow():
        revoke_refresh_token(db, jti)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    new_access = create_access_token({"sub": payload["sub"]})
    return {
    "access_token": new_access,
    "token_type": "bearer",
    "refresh_token": refresh_token.refresh_token
    }

@router.post("/token/revoke")
def revoke_token_endpoint(refresh_token: RefreshRequest, db: Session = Depends(get_db)):
    payload = verify_token(refresh_token.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    jti = payload.get("jti")
    success = revoke_refresh_token(db, jti)
    if not success:
        return {"detail": "Token not found or already revoked"}
    return {"detail": "Token revoked"}
