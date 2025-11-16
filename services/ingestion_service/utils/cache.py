import json
import redis.asyncio as redis
from os import getenv

REDIS_HOST = getenv("REDIS_HOST")
REDIS_PORT = int(getenv("REDIS_PORT"))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

async def set_historical(symbol: str, interval: str, value: list, ex: int = 60):
    await r.set(f"historical:{symbol}:{interval}", json.dumps(value), ex=ex)

async def get_historical(symbol: str, interval: str):
    data = await r.get(f"historical:{symbol}:{interval}")
    return json.loads(data) if data else None

async def append_historical(symbol: str, interval: str, new_data_point: dict, ex: int = 60):
    key = f"historical:{symbol}:{interval}"
    data = await r.get(key)
    historical_list = json.loads(data) if data else []
    historical_list.append(new_data_point)
    historical_list = historical_list[-500:]
    await r.set(key, json.dumps(historical_list), ex=ex)
    return historical_list