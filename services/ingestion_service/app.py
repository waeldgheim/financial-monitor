from fastapi import FastAPI
from routes.ingestion_routes import router as ingestion_router
from utils.workers import start_background_tasks
from shared_lib.db import engine
from models import Base

app = FastAPI(title="Ingestion Service")
app.include_router(ingestion_router, prefix="/api/data", tags=["ingestion"])

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    # start background listeners
    print("🚀 Starting background tasks...", flush=True)
    await start_background_tasks()
    print("✅ Background tasks launched", flush=True)
