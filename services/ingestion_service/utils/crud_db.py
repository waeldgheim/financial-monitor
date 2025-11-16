from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from models import Crypto, Stock

def insert_crypto_data(db: Session, crypto_data: dict):
    stmt = insert(Crypto).values(**crypto_data)
    stmt = stmt.on_conflict_do_nothing()
    db.execute(stmt)
    db.commit()

def get_crypto_data(db: Session, symbol: str):
    return db.query(Crypto).filter(Crypto.symbol == symbol).all()

def insert_stock_data(db: Session, stock_data: dict):
    stmt = insert(Stock).values(**stock_data)
    stmt = stmt.on_conflict_do_nothing()
    db.execute(stmt)
    db.commit()

def get_stock_data(db: Session, symbol: str):
    return db.query(Stock).filter(Stock.symbol == symbol).all()