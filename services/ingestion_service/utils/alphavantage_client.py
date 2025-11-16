import httpx, asyncio
from os import getenv
from utils.cache import set_historical, append_historical
from utils.broadcast import broadcast_update
from datetime import datetime, timezone
from utils.crud_db import insert_stock_data
from shared_lib.db import SessionLocal

ALPHAVANTAGE_KEY = getenv("ALPHAVANTAGE_API_KEY")
ALPHAVANTAGE_URL = getenv("ALPHAVANTAGE_URL_BASE")

async def fetch_alpha_intraday(symbol: str, interval="1min", poller=False):

    params = {"function":"TIME_SERIES_INTRADAY", "symbol":symbol, "interval":interval, "apikey":ALPHAVANTAGE_KEY, "outputsize":"compact"}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(ALPHAVANTAGE_URL, params=params)
        r.raise_for_status()
        data = r.json()
    key = f"Time Series ({interval})"
    series = data.get(key) or {}
    # Convert to list of candles (sorted ascending)
    klines = []
    for ts, vals in sorted(series.items()):
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(tzinfo=timezone.utc)
        open_time_ms = int(dt.timestamp() * 1000)
        data = {
            "symbol": symbol,
            "open_time": open_time_ms,
            "open": float(vals["1. open"]),
            "high": float(vals["2. high"]),
            "low": float(vals["3. low"]),
            "close": float(vals["4. close"]),
            "volume": float(vals["5. volume"])
        }
        klines.append(data)
    if not poller:
        with SessionLocal() as db:
            for data_point in klines:
                insert_stock_data(db, data_point)
    await set_historical(symbol, "1m", klines, ex=86400)
    return klines

async def alphavantage_poller(symbols=["AAPL","SPY"], interval="1min"):
    while True:
        for symbol in symbols:
            try:
                klines = await fetch_alpha_intraday(symbol, interval=interval, poller=True)
                if klines:
                    latest = klines[-1]
                    with SessionLocal() as db:
                        insert_stock_data(db, latest)
                    await append_historical(symbol, "1m", latest, ex=86400)
                    await broadcast_update(symbol.upper(), latest)
            except Exception as e:
                print("Alpha fetch error for", symbol, e)
        await asyncio.sleep(60)
