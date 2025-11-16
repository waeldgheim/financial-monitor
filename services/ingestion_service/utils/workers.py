import asyncio
from utils.binance_client import binance_ws_listener
from utils.alphavantage_client import alphavantage_poller

background_tasks = []

async def start_background_tasks():
    loop = asyncio.get_running_loop()
    t1 = loop.create_task(binance_ws_listener(symbols=["btcusdt","ethusdt"], interval="1m"))
    t2 = loop.create_task(alphavantage_poller(symbols=["AAPL","SPY"], interval="1min"))
    background_tasks.extend([t1,t2])
