from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from shared_lib.db import SessionLocal
from models import User
from crud import create_user
from schemas import UserCreate, UserResponse


router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users")
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, username=user.username, email=user.email, password=user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return user