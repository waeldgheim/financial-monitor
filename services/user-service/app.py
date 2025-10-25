from fastapi import FastAPI
from routes.user_routes import router as user_router
from models import Base
from db import engine

app = FastAPI(title="User Service")

# Create tables
Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(user_router, prefix="/api/users", tags=["users"])
