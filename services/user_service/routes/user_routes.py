from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
from sqlalchemy.orm import Session
from shared_lib.db import SessionLocal
from models import User
from crud import create_user, authenticate_user
from schemas import UserCreate, TokenResponse, LoginRequest, UserProfile
from utils import create_access_token, verify_token
from datetime import timedelta


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
    token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": token}

@router.post("/login", response_model=TokenResponse)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, email=request.email, password=request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        ) 
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token}

@router.get("/profile", response_model=UserProfile)
def read_profile(current_user: User = Depends(get_current_user)):
    return current_user