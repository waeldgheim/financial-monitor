from fastapi import APIRouter, WebSocket
from utils.cache import get_historical
from utils.broadcast import register, unregister
from utils.binance_client import fetch_binance_klines
from utils.alphavantage_client import fetch_alpha_intraday
from utils.cache import set_historical

router = APIRouter()

@router.get("/{symbol}/historical")
async def get_historical_endpoint(symbol: str, interval: str = "1m", limit: int = 500):
    symbol = symbol.upper()
    cached = await get_historical(symbol, interval)
    if cached:
        return cached[-limit:]
    klines = None
    if symbol.endswith("USDT"):   # crypto → Binance
        klines = await fetch_binance_klines(symbol, interval=interval, limit=limit)
    else:                         # equity → AlphaVantage
        klines = await fetch_alpha_intraday(symbol, interval=interval)
    if klines:
        await set_historical(symbol, interval, klines, ex=3600)
    return klines or []

@router.websocket("/ws/stream")
async def websocket_stream(ws: WebSocket):
    # protocol: client must send {"action":"subscribe", "symbols":["BTCUSDT","AAPL"]} as JSON
    await ws.accept()
    try:
        msg = await ws.receive_json()
        if msg.get("action") == "subscribe":
            symbols = [s.upper() for s in msg.get("symbols",[])]
            await register(ws, symbols)
            while True:
                await ws.receive_text()
    except Exception:
        pass
    finally:
        await unregister(ws)
