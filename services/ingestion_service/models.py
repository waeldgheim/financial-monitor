from sqlalchemy import Column, BigInteger, String, Float
from shared_lib.models import Base

class Crypto(Base):
    __tablename__ = 'cryptos'

    symbol = Column(String(32), index=True, nullable=False, primary_key=True)
    start_time = Column(BigInteger, index=True, nullable=False, primary_key=True)
    end_time = Column(BigInteger, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

class Stock(Base):
    __tablename__ = 'stocks'

    symbol = Column(String, index=True, nullable=False, primary_key=True)
    open_time = Column(BigInteger, index=True, nullable=False, primary_key=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)