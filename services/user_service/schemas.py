# user-service/models.py
from pydantic import BaseModel, EmailStr, validator
from fastapi import HTTPException, status
import re
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator("password")
    def validate_password_strength(cls, v):
        # Must contain uppercase, lowercase, number, and special character
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$"
        if not re.match(pattern, v) or len(v) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must have at least 8 characters and contain at least one uppercase letter, one lowercase letter, one number, and one special character."
            )
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str

class UserProfile(BaseModel):
    username: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True
