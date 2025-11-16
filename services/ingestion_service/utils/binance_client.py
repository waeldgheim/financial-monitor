import httpx
from os import getenv
import websockets
import asyncio
from shared_lib.db import SessionLocal
from utils.broadcast import broadcast_update
from utils.cache import set_historical, append_historical
import json
from utils.crud_db import insert_crypto_data

BASE = getenv("BINANCE_REST_BASE")
WS_BASE = getenv("BINANCE_WS_BASE")

async def fetch_binance_klines(symbol="BTCUSDT", interval="1m", limit=500):
    url = f"{BASE}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        raw = r.json()
    klines = []
    with SessionLocal() as db:
        for k in raw:
            data = {
                "symbol": symbol,
                "open_time": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
                "close_time": k[6],
            }
            insert_crypto_data(db, data)
        klines.append(data)
    await set_historical(symbol, interval, klines, ex=86400) 
    return klines

async def binance_ws_listener(symbols=["btcusdt","ethusdt"], interval="1m"):
    streams = "/".join(f"{s}@kline_{interval}" for s in symbols)
    ws_url = f"{WS_BASE}?streams={streams}"
    retry_delay = 5
    while True:
        try:
            print("🔌 Connecting to Binance WebSocket...")
            async with websockets.connect(ws_url) as ws:
                print("✅ Connected to Binance", flush=True)
                async for msg in ws:
                    try:
                        data = json.loads(msg)
                    except json.JSONDecodeError:
                        print("❌ JSON parse error", flush=True)
                        continue
                    payload = data.get("data") or data
                    k = payload.get("k")
                    if not k or not k["x"]:
                        continue
                    try:
                        symbol = k.get("s")
                        candle = {
                            "symbol": symbol,
                            "start_time": k["t"],
                            "end_time": k["T"],
                            "open": float(k["o"]),
                            "high": float(k["h"]),
                            "low": float(k["l"]),
                            "close": float(k["c"]),
                            "volume": float(k["v"])
                        }
                        with SessionLocal() as db:
                            insert_crypto_data(db, candle)
                        await append_historical(symbol, interval, candle, ex=86400)
                        await broadcast_update(symbol, candle)
                    except KeyError:
                        print("❌ Missing candle field", flush=True)
                        continue
        except asyncio.CancelledError:
            print("🛑 Binance WS listener cancelled", flush=True)
            break

        except Exception as e:
            print("🔥 Binance WS error:", e, flush=True)
            print(f"⏳ Reconnecting in {retry_delay}s...", flush=True)
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)