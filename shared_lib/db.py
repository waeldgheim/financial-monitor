# shared_lib/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import getenv

engine = create_engine(getenv("DATABASE_URL"), echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
